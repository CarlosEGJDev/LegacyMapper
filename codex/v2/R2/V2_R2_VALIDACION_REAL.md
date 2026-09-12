STATUS: PASS

METRICS:
  repository:
    total_files: 14355
    vb_source: 4328
    webforms_total: 3346
    webforms_with_codebehind: 3146
  entry_points:
    total: 12662
    confirmed: 12642
    unresolved: 20
    by_type:
      web_event: 7723
      web_lifecycle: 4939
    unique_webforms_with_entry_points: 2580
    unique_controls: 1572
    unique_handlers: 1655
    handlers_with_outgoing_calls: 11322
  event_bindings:
    total: 12662
    confirmed: 12642
    unresolved: 20
    vb_handles_bindings: 12626
    markup_on_event_bindings: 35
    lifecycle_bindings: 4939
  functional_dependencies:
    total: 231510
    webform_to_event_edges: 12658
    event_to_handler_edges: 12662
    handler_to_method_edges: 12597
    duplicate_logical_edges: 0
  errors:
    total: 0
  r1_1_regression_baseline:
    R1_1_calls_total: 230355
    R2_calls_total: 230355
    R1_1_confirmed_calls: 12775
    R2_confirmed_calls: 12775
    R1_1_cross_project_confirmed: 9293
    R2_cross_project_confirmed: 9293
    R1_1_duplicate_dependency_edges: 0
    R2_duplicate_dependency_edges: 0

COVERAGE:
  webforms_total: 3346
  webforms_with_codebehind: 3146
  webforms_with_entry_points: 2580
  handles_textual_lines_found_by_rg: 12702
  vb_handles_bindings_extracted: 12626
  handles_me_load_textual_lines: 146
  handles_mybase_load_textual_lines: 2426
  multiple_handles_textual_lines: 29
  overrides_lifecycle_textual_lines: 1
  markup_on_event_textual_lines: 28
  markup_events_in_webforms_json: 40
  markup_event_bindings: 35
  major_gaps:
    - Some WebForms have no deterministic codebehind/class/handler evidence; absence of events is not treated as failure.
    - Dynamic AddHandler wiring is not supported by design.
    - Some unresolved markup events are client-side HTML onclick or have missing handler methods.
    - Source project remains null for duplicated/root-level legacy files not deterministically owned by a vbproj.
  assessment: coverage is sufficient for R2 real validation.

CONFIRMED_SAMPLE:
  sampled: 25
  correct: 23
  suspicious: 2
  incorrect: 0
  observed_precision_estimate: 0.92
  note: sampling estimate only; not global proof.
  samples:
    - CORRECT | ucADHActualizaTasas.ascx -> btnProcesar.Click -> btnProcesar_Click -> class ucADHActualizaTasas | evidence: Protected Sub ... Handles btnProcesar.Click | outgoing_calls: 3
    - CORRECT | ucADHActualizaTasas.ascx -> btnSimular.Click -> btnSimular_Click -> class ucADHActualizaTasas | outgoing_calls: 3
    - CORRECT | ucADHActualizaTasas.ascx -> btnCancelar.Click -> btnCancelar_Click -> class ucADHActualizaTasas | outgoing_calls: 1
    - CORRECT | ucADHActualizaTasas.ascx -> btnContinuar.Click -> btnContinuar_Click -> class ucADHActualizaTasas | outgoing_calls: 9
    - CORRECT | ucADHActualizaTasasRecal.ascx -> btnBuscar.Click -> btnBuscar_Click -> class ucADHActualizaTasasRecal | outgoing_calls: 1
    - CORRECT | ucADHActualizaTasasRecal.ascx -> btnLimpiar.Click -> btnLimpiar_Click -> class ucADHActualizaTasasRecal | outgoing_calls: 1
    - CORRECT | ucADHActualizaTasasRecal.ascx -> btnProcesar.Click -> btnProcesar_Click -> class ucADHActualizaTasasRecal | outgoing_calls: 1
    - CORRECT | ucADHActualizaTasasRecal.ascx -> btnExcel.Click -> btnExcel_Click -> class ucADHActualizaTasasRecal | outgoing_calls: 1
    - CORRECT | PreImpresion.ascx -> MyBase.Init -> Page_Init -> class PreImpresion | web_lifecycle | outgoing_calls: 1
    - CORRECT | PreImpresion.ascx -> MyBase.Load -> Page_Load -> class PreImpresion | web_lifecycle
    - CORRECT | testUserControl.aspx -> MyBase.Init -> Page_Init -> class testUserControl | web_lifecycle | outgoing_calls: 1
    - CORRECT | testUserControl.aspx -> MyBase.Load -> Page_Load -> class testUserControl | web_lifecycle
    - CORRECT | ucADHActualizaTasas.ascx -> MyBase.Init -> Page_Init -> class ucADHActualizaTasas | web_lifecycle
    - CORRECT | ucADHActualizaTasas.ascx -> MyBase.Load -> Page_Load -> class ucADHActualizaTasas | outgoing includes confirmed BL call txtraerPereva
    - CORRECT | WebCobMantencion\cobInformeDeudasDT.ascx -> txtFecPago.TextChanged -> txtFecPago_TextChanged -> class cobInformeDeudasDT | markup OnTextChanged
    - CORRECT | WebHISTCalificacionRECA\ucRegularizarRecaAvanzado.ascx -> txtCun.TextChanged -> txtItem_TextChanged | markup OnTextChanged
    - CORRECT | WebHISTCalificacionRECA\ucRegularizarRecaAvanzado.ascx -> txtFolAte.TextChanged -> txtItem_TextChanged | markup OnTextChanged
    - CORRECT | WebHISTCalificacionRECA\ucRegularizarRecaAvanzado.ascx -> txtRutPer.TextChanged -> txtItem_TextChanged | markup OnTextChanged
    - CORRECT | WebHISTCalificacionRECA\ucRegularizarRecaAvanzado.ascx -> ddlIndTipPac.TextChanged -> txtItem_TextChanged | markup OnTextChanged
    - CORRECT | WebHISTCalificacionRECA\ucRegularizarRecaAvanzado.ascx -> ddlIndCauCon.TextChanged -> txtItem_TextChanged | markup OnTextChanged
    - CORRECT | WebHISTCalificacionRECA\ucRegularizarRecaAvanzado.ascx -> txtDiasPerdidos.TextChanged -> txtItem_TextChanged | markup OnTextChanged
    - CORRECT | WebHISTCalificacionRECA\ucRegularizarRecaAvanzado.ascx -> txtLey77Bis.TextChanged -> txtItem_TextChanged | markup OnTextChanged
    - SUSPICIOUS | ucADHActualizaTasas.ascx -> chkMasivo.CheckedChanged -> chkMasivo_CheckedChanged | class resolved, project null due unresolved source ownership
    - SUSPICIOUS | ucADHActualizaTasasRecal.ascx -> chkTodos.CheckedChanged -> chkMasivo_CheckedChanged | multiple Handles-like handler name is valid, project null due unresolved source ownership
    - CORRECT | webMEDValorizacion\ucValMo055.ascx -> PreRender -> OnPreRender | evidence: Protected Overrides Sub OnPreRender(...)

CALL_GRAPH_CONNECTION:
  sampled_confirmed_handlers_with_outgoing_calls: 15
  assessment: PASS
  examples:
    - entry: ucADHActualizaTasas.ascx MyBase.Load Page_Load
      outgoing:
        - SetFocusControl | unresolved
        - Mostrar_Confirmacion | unresolved
        - Bl.ADHAdmCalculoDs67.blADHds67.txtraerPereva | confirmed -> Sonda.Gestion.Nssmut.Bl.ADHAdmCalculoDs67.blADHds67.txtraerpereva
    - entry: ucADHActualizaTasas.ascx btnProcesar.Click btnProcesar_Click
      outgoing:
        - Parametros_Ok | unresolved
        - Mostrar_Confirmacion | unresolved
    - entry: ucADHActualizaTasas.ascx btnContinuar.Click btnContinuar_Click
      outgoing:
        - wsproce.wmInicializarProceso | unresolved
        - wsproce.wmProgramarEtapa | unresolved
    - entry: ucADHActualizaTasasRecal.ascx MyBase.Load Page_Load
      outgoing:
        - Lee_Parametros | unresolved
        - LLena_Fechas | unresolved
    - entry: ucADHActualizaTasasRecal.ascx btnBuscar.Click btnBuscar_Click
      outgoing:
        - Lee_Datos | unresolved
    - entry: ucADHActualizaTasasRecal.ascx btnProcesar.Click btnProcesar_Click
      outgoing:
        - Procesar_Actualizacion_Tasas | unresolved
    - entry: ucADHAnexoDEU.ascx MyBase.Load Page_Load
      outgoing:
        - Lee_Datos | unresolved
    - entry: ucADHAnexoDEU.ascx btnVolver.Click btnVolver_Click
      outgoing:
        - dspar1.Dispose | unresolved
        - Server.Transfer | unresolved
    - entry: ucADHAnexoNOM.ascx MyBase.Load Page_Load
      outgoing:
        - Lee_Datos | unresolved
    - entry: ucADHAnexoNOM.ascx btnVolver.Click btnVolver_Click
      outgoing:
        - dsPar1.Dispose | unresolved
        - Server.Transfer | unresolved
    - entry: ucADHAnexoPAT.ascx MyBase.Load Page_Load
      outgoing:
        - Lee_Datos | unresolved
    - entry: ucADHActualizaTasasRecal.ascx ddlPerEva.SelectedIndexChanged ddlPerEva_SelectedIndexChanged
      outgoing:
        - LLena_Fechas | unresolved
    - entry: ucADHActualizaTasasRecal.ascx DataGrid1.ItemDataBound DataGrid1_ItemDataBound
      outgoing:
        - FormatRut | unresolved
    - entry: ucADHActualizaTasasRecal.ascx btnExcel.Click btnExcel_Click
      outgoing:
        - Lee_Excel | unresolved
    - entry: PreImpresion.ascx MyBase.Init Page_Init
      outgoing:
        - InitializeComponent | unresolved
  note:
    - R2 correctly links EntryPoint -> Handler -> existing outgoing_calls.
    - Many outgoing calls remain unresolved because call resolution belongs to V2-R1.x/R4, not R2.
    - No recursive flow construction was performed.

FALSE_POSITIVES:
  arbitrary_click_methods_without_binding:
    finding: no evidence of mass false-positive _Click inference; entry points require Handles or markup evidence.
    click_entry_points: 4441
  javascript_mistaken_as_event:
    js_in_event_evidence: 0
    status: PASS
  comments_mistaken_as_bindings:
    finding: no sampled evidence; VB event extractor strips comments before Handles parsing.
  markup_text_mistaken_as_attributes:
    malformed_markup_handlers: 0
    status: PASS
  lifecycle_confirmed_only_by_name:
    lifecycle_without_handles_or_overrides: 0
    status: PASS
  duplicate_event_bindings:
    duplicate_entry_point_keys: 0
    duplicate_event_binding_keys: 0
    status: PASS
  handler_wrong_class_or_webform:
    sampled_incorrect: 0
    residual_risk: source project may be null for unowned duplicated files, but class/handler relation is deterministic.
  malformed_on_event_interpretation:
    html_img_onclick_unresolved: 12
    status: NON_BLOCKING_NOISE
    note: client-side IMG onclick is captured as unresolved event binding; should be filtered in a cleanup pass but does not authorize false confirmed relations.

FALSE_NEGATIVES:
  handles_control_event:
    textual_lines: 12702
    extracted_vb_handles_bindings: 12626
    assessment: low_miss_rate_or_textual_overcount
  handles_me_load:
    textual_lines: 146
    covered_by_lifecycle: yes
  handles_mybase_load:
    textual_lines: 2426
    covered_by_lifecycle: yes
  multiple_handles:
    textual_lines: 29
    supported: yes
  markup_onclick:
    supported: yes
  markup_other_on_event:
    supported_examples:
      - OnTextChanged
      - OnSelectedIndexChanged
      - OnMenuItemClick
      - OnCreatedUser
  overrides_lifecycle:
    textual_lines: 1
    confirmed_sample: webMEDValorizacion\ucValMo055.ascx OnPreRender
  accepted_limitations:
    - AddHandler not supported.
    - dynamic event wiring not supported.
    - designer/control tree wiring not supported.
  material_false_negative_defect: false

UNRESOLVED:
  total_unresolved_entry_points: 20
  causes:
    client_side_html_onclick:
      count: 12
      examples:
        - Menu3Horizontalswitch.ascx onclick=rf_divCloseMenuHorizontal_click
        - Menu3Verticalswitch.ascx onclick=rf_divCloseMenuVertical_click
      assessment: should_filter_later
    markup_handler_missing_or_unresolved:
      count: 8
      examples:
        - WebTransmisionMan\ucAnularCompDup.ascx btnConfirmarEliminar_Click
        - WebTransmisionMan\WebTraManMedicos2.ascx btnConsultar_Click
        - proyectos\slnCOTMantenciones\slnCOTMantenciones\Account\Register.aspx RegisterUser_CreatedUser
      assessment: healthy_conservatism
  overall_assessment: unresolved is conservative and non-blocking.

REGRESSION:
  v2_r1_1_call_graph:
    calls_total_consistent: true
    confirmed_calls_consistent: true
    cross_project_confirmed_consistent: true
    multiple_candidate_calls_consistent: true
  functional_dependency_dedup:
    R1_1_duplicate_edges: 0
    R2_duplicate_edges: 0
    status: PASS
  errors:
    R1_1_errors: 0
    R2_errors: 0
    status: PASS
  assessment: no V2-R1.1 regression detected.

SANITY:
  top_webforms_by_entry_points:
    - webPENCalculoPensionIndem\ucPENMARPE.ascx: 111
    - webADHSolicitud2\ucADHSociosCubiertos.ascx: 33
    - proyectos\slnADHSolicitud2\Backup\WebADHSolicitud2\WebADHSolicitud2\ucADHSociosCubiertos.ascx: 33
    - webADHSolicitud2\ucADHSolTrb2.ascx: 30
    - webCOTRecepcion\ucCotMo090.ascx: 30
  top_handlers:
    - Page_Load: 2587
    - Page_Init: 2326
    - hypBuscar_Click: 430
    - btnBuscar_Click: 309
    - btnGuardar_Click: 209
  top_events:
    - MyBase.Load: 2423
    - MyBase.Init: 2326
    - hypBuscar.Click: 434
    - btnBuscar.Click: 313
    - hypGuardar.Click: 211
  lifecycle_explosion: false
  repeated_identical_bindings: false
  unexpected_global_hotspot: false
  notes:
    - Page_Load/Page_Init hotspots are expected in WebForms.
    - Large WebForms with many controls/events exist but are plausible in legacy UI.

REQUIRED_FIXES:
  CRITICAL: []
  HIGH: []
  MEDIUM:
    - Filter client-side HTML attributes such as lowercase onclick on non-server HTML tags from event_bindings, or classify them separately as client-side/unresolved.
    - Improve source project ownership for duplicated/root-level WebForms where class/handler resolves but project remains null.
    - Add a metrics summary index for entry point coverage to simplify future validations.
  LOW:
    - Normalize binding_kind explicitly in event_bindings instead of inferring from evidence text.
    - Preserve direct codebehind/class link records as a separate index if later documentation needs them.

DECISION: A) V2-R2_APROBADA_PARA_R3
