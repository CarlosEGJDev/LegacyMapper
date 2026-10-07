"""Provider-neutral input ceiling; approved V4.3 output reservation policy."""
DEFAULT_MAX_REQUEST_PAYLOAD_TOKENS = 16000

def payload_token_limit(provider: object, request_max_output_tokens: int | None = None) -> int:
    """The applicable ceiling for the final INPUT payload, in estimated tokens.

    Policy (V4.3-R5, this correction):

    - A provider that declares no valid `context_window` (not an `int > 0`)
      gets LegacyMapper's own `DEFAULT_MAX_REQUEST_PAYLOAD_TOKENS` ceiling on
      the input payload, unchanged from before this correction. That ceiling
      is never widened by anything below.
    - A provider that DOES declare a valid `context_window` shares that same
      window between the input payload and whatever output the provider may
      still need to produce afterwards. Authorizing an input payload up to
      the full `context_window` -- the pre-correction behavior -- could
      therefore authorize `input_tokens + max_output_tokens > context_window`
      once the provider actually generates. This function instead reserves
      output capacity first and returns the remainder:

          effective_input_limit = context_window - reserved_output_tokens

      `reserved_output_tokens` is chosen deterministically: prefer the
      provider's own declared `capabilities().max_output_tokens` when it is a
      valid `int > 0`; if the caller additionally knows the specific
      request's `max_output_tokens` and it is a smaller valid positive int,
      that smaller value is the reservation instead, since it is what that
      particular request could actually still produce. A provider that
      declares neither reserves nothing extra (`reserved_output_tokens = 0`)
      -- there is no further explicit, deterministic figure to reserve
      against, and LegacyMapper does not guess one.
    - The effective limit returned here can be zero or negative when the
      reservation consumes the whole window or more; callers MUST fail
      closed (`CONTEXT_TOO_LARGE`) on that rather than passing a
      non-positive limit through to a size comparison, since no input
      payload, however small, could ever fit alongside that reservation.
      This function itself never raises for that case -- it reports the
      number so the caller can gate on it before doing any other work.
    """
    try:
        capabilities = provider.capabilities()
        window = getattr(capabilities, "context_window", None)
    except Exception:
        capabilities = None
        window = None
    if not (isinstance(window, int) and window > 0):
        return DEFAULT_MAX_REQUEST_PAYLOAD_TOKENS

    declared_output = getattr(capabilities, "max_output_tokens", None) if capabilities is not None else None
    reserved = declared_output if isinstance(declared_output, int) and declared_output > 0 else 0
    if (
        isinstance(request_max_output_tokens, int)
        and request_max_output_tokens > 0
        and request_max_output_tokens < reserved
    ):
        reserved = request_max_output_tokens

    return window - reserved


