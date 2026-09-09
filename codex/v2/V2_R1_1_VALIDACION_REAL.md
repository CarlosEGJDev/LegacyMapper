STATUS: PASS

METRICS_COMPARISON:
  R1:
    total_calls: 453574
    confirmed: 10909
    inferred: 210786
    unresolved: 231879
    confirmed_pct: 2.41
    inferred_pct: 46.47
    unresolved_pct: 51.12
    instantiations: 40279
    functional_dependencies_total: 532200
    duplicate_logical_dependency_keys: 56114
    duplicate_extra_rows: 290389
    cross_project_confirmed: 7841
    unique_resolved_targets: 32611
    multiple_candidate_calls: 8808
    errors: 0
  R1_1:
    total_calls: 230355
    confirmed: 12775
    inferred: 0
    unresolved: 217580
    confirmed_pct: 5.55
    inferred_pct: 0.00
    unresolved_pct: 94.45
    instantiations: 40279
    functional_dependencies_total: 193593
    duplicate_logical_dependency_keys: 0
    duplicate_extra_rows: 0
    cross_project_confirmed: 9293
    unique_resolved_targets: 3981
    multiple_candidate_calls: 4852
    errors: 0
  assessment:
    noise_reduction: STRONG
    valid_resolution_preservation: PRESERVED_OR_IMPROVED
    notes:
      - total_calls reduced by 223219 rows.
      - inferred calls reduced from 210786 to 0.
      - confirmed calls increased from 10909 to 12775.
      - functional_dependencies reduced from 532200 to 193593.
      - duplicate logical dependency rows reduced to 0.
      - cross_project_confirmed increased from 7841 to 9293.

REGRESSION_CHECKS:
  vb_builtins_intrinsics:
    R1_builtin_calls: 108699
    R1_1_builtin_calls: 0
    status: PASS
    checked_names:
      - IsNothing
      - CStr
      - CInt
      - CDate
      - CDbl
      - CDec
      - IIf
      - Format
      - DateAdd
      - CType
      - DirectCast
      - TryCast
      - GetType
      - IsDate
  javascript_string_literal_calls:
    R1_lines_with_javascript_in_evidence: 5792
    R1_1_lines_with_javascript_in_evidence: 172
    status: PASS_WITH_RESIDUAL_NON_BLOCKING
    notes:
      - residual samples are real VB calls on lines that also contain javascript strings, e.g. tpaBusEmpresa.ColumnaPorId(...), not extracted JavaScript function names.
      - artificial JavaScript targets such as OnClickWindowOpen/onGuardarOff/onMensajeOff are no longer present in inferred output because inferred output is 0.
  indexed_default_property_false_calls:
    R1_index_calls: 86855
    R1_1_index_calls: 0
    status: PASS
    checked_names:
      - Tables
      - Rows
      - Item
      - Items
      - Attributes
      - Session
  artificial_inferred_targets:
    R1_inferred: 210786
    R1_1_inferred: 0
    status: PASS
    examples_removed:
      - Class.isnothing
      - Class.cstr
      - Class.values
      - Class.format
  duplicated_class_uses_edges:
    R1_duplicate_extra_rows: 290389
    R1_1_duplicate_extra_rows: 0
    status: PASS
  fully_qualified_receiver_preservation:
    status: PASS
    sample:
      file: webADHAdmCalculoDs67\ucADHActualizaTasas.ascx.vb
      line: 61
      expression: Bl.ADHAdmCalculoDs67.blADHds67.txtraerPereva(2)
      receiver: blADHds67
      receiver_path: Bl.ADHAdmCalculoDs67.blADHds67
      resolved_target: Sonda.Gestion.Nssmut.Bl.ADHAdmCalculoDs67.blADHds67.txtraerpereva

CONFIRMED_SAMPLE:
  summary:
    sampled: 25
    correct: 23
    suspicious: 2
    incorrect: 0
    observed_precision_estimate: 0.92
    note: sampling estimate only; not global proof.
  samples:
    - status: CORRECT
      evidence: bl\blPistCargaArchSisesat.vb:223
      source_project: bl\BlCargaSISESAT.vbproj
      target_project: bl\blParGenerales\blParGenerales.vbproj
      receiver_path: Bl.ParametrosGenerales.ParRuta
      method: txtraer
      target: Sonda.Gestion.Nssmut.Bl.ParametrosGenerales.ParRuta.txtraer
    - status: CORRECT
      evidence: webADHAdmCalculoDs67\ucADHActualizaTasas.ascx.vb:61
      source_project: WebADHAdmCalculoDs67.vbproj
      target_project: bl\blADHAdmCalculoDs67\blADHAdmCalculoDs67.vbproj
      receiver_path: Bl.ADHAdmCalculoDs67.blADHds67
      method: txtraerPereva
      target: Sonda.Gestion.Nssmut.Bl.ADHAdmCalculoDs67.blADHds67.txtraerpereva
    - status: CORRECT
      evidence: webADHAdmCalculoDs67\ucADHActualizaTasas.ascx.vb:124
      source_project: WebADHAdmCalculoDs67.vbproj
      target_project: bl\blADHAdmCalculoDs67\blADHAdmCalculoDs67.vbproj
      receiver_path: Bl.ADHAdmCalculoDs67.blADHds67
      method: txTraerDatosRut
      target: Sonda.Gestion.Nssmut.Bl.ADHAdmCalculoDs67.blADHds67.txtraerdatosrut
    - status: CORRECT
      evidence: webADHAdmCalculoDs67\ucADHActualizaTasasRecal.ascx.vb:80
      source_project: WebADHAdmCalculoDs67.vbproj
      target_project: bl\blADHAdmCalculoDs67\blADHAdmCalculoDs67.vbproj
      receiver_path: Bl.ADHAdmCalculoDs67.blADHds67
      method: txtraerPereva
      target: Sonda.Gestion.Nssmut.Bl.ADHAdmCalculoDs67.blADHds67.txtraerpereva
    - status: CORRECT
      evidence: webADHAdmCalculoDs67\ucADHAnexoDEU.ascx.vb:58
      source_project: WebADHAdmCalculoDs67.vbproj
      target_project: bl\blADHAdmCalculoDs67\blADHAdmCalculoDs67.vbproj
      receiver_path: Bl.ADHAdmCalculoDs67.blUtil
      method: CargaCamposFormulario
      target: Sonda.Gestion.Nssmut.Bl.ADHAdmCalculoDs67.blUtil.cargacamposformulario
    - status: CORRECT
      evidence: webADHAdmCalculoDs67\ucADHAnexoNOM.ascx.vb:61
      source_project: WebADHAdmCalculoDs67.vbproj
      target_project: bl\blADHAdmCalculoDs67\blADHAdmCalculoDs67.vbproj
      receiver_path: Bl.ADHAdmCalculoDs67.blUtil
      method: CargaCamposFormulario
      target: Sonda.Gestion.Nssmut.Bl.ADHAdmCalculoDs67.blUtil.cargacamposformulario
    - status: CORRECT
      evidence: webADHAdmCalculoDs67\ucADHAnexoPAT.ascx.vb:282
      source_project: WebADHAdmCalculoDs67.vbproj
      target_project: bl\blADHAdmCalculoDs67\blADHAdmCalculoDs67.vbproj
      receiver_path: Bl.ADHAdmCalculoDs67.blUtil
      method: CargaCamposFormulario
      target: Sonda.Gestion.Nssmut.Bl.ADHAdmCalculoDs67.blUtil.cargacamposformulario
    - status: CORRECT
      evidence: webADHAdmCalculoDs67\ucADHCargaTasaHistorica.ascx.vb:90
      source_project: WebADHAdmCalculoDs67.vbproj
      target_project: bl\blParGenerales\blParGenerales.vbproj
      receiver_path: Bl.ParametrosGenerales.ParRuta
      method: txtraer
      target: Sonda.Gestion.Nssmut.Bl.ParametrosGenerales.ParRuta.txtraer
    - status: CORRECT
      evidence: webADHAdmCalculoDs67\ucADHCargaTasaHistorica.ascx.vb:162
      source_project: WebADHAdmCalculoDs67.vbproj
      target_project: bl\blADHAdmCalculoDs67\blADHAdmCalculoDs67.vbproj
      receiver_path: Bl.ADHAdmCalculoDs67.blPadhD67Rut
      method: txLeeEstadoCargaTasa
      target: Sonda.Gestion.Nssmut.Bl.ADHAdmCalculoDs67.blPadhD67Rut.txleeestadocargatasa
    - status: CORRECT
      evidence: webADHAdmCalculoDs67\ucADHCargaTasaHistorica.ascx.vb:276
      source_project: WebADHAdmCalculoDs67.vbproj
      target_project: bl\blADHAdmCalculoDs67\blADHAdmCalculoDs67.vbproj
      receiver_path: Bl.ADHAdmCalculoDs67.blPadhD67Rut
      method: txCargarAdhTasas
      target: Sonda.Gestion.Nssmut.Bl.ADHAdmCalculoDs67.blPadhD67Rut.txcargaradhtasas
    - status: CORRECT
      evidence: webADHAdmCalculoDs67\ucADHCargaTasaHistorica.ascx.vb:331
      source_project: WebADHAdmCalculoDs67.vbproj
      target_project: bl\blADHAdmCalculoDs67\blADHAdmCalculoDs67.vbproj
      receiver_path: Bl.ADHAdmCalculoDs67.blPadhD67Rut
      method: txReversarAdhTasas
      target: Sonda.Gestion.Nssmut.Bl.ADHAdmCalculoDs67.blPadhD67Rut.txreversaradhtasas
    - status: CORRECT
      evidence: webADHAdmCalculoDs67\ucADHCartasDefine.ascx.vb:111
      source_project: WebADHAdmCalculoDs67.vbproj
      target_project: bl\blParGenerales\blParGenerales.vbproj
      receiver_path: Bl.ParametrosGenerales.ParNum
      method: txLlenarDropDownList
      target: Sonda.Gestion.Nssmut.Bl.ParametrosGenerales.ParNum.txllenardropdownlist
    - status: SUSPICIOUS
      evidence: ucADHActualizaTasas.ascx.vb:61
      source_project: null
      target_project: bl\blADHAdmCalculoDs67\blADHAdmCalculoDs67.vbproj
      receiver_path: Bl.ADHAdmCalculoDs67.blADHds67
      method: txtraerPereva
      target: Sonda.Gestion.Nssmut.Bl.ADHAdmCalculoDs67.blADHds67.txtraerpereva
      reason: target exists, but source project association is absent.
    - status: SUSPICIOUS
      evidence: ucADHActualizaTasas.ascx.vb:124
      source_project: null
      target_project: bl\blADHAdmCalculoDs67\blADHAdmCalculoDs67.vbproj
      receiver_path: Bl.ADHAdmCalculoDs67.blADHds67
      method: txTraerDatosRut
      target: Sonda.Gestion.Nssmut.Bl.ADHAdmCalculoDs67.blADHds67.txtraerdatosrut
      reason: target exists, but source project association is absent.
    - status: CORRECT
      evidence: bl\blPistCargaArchSisesat.vb:103
      source_project: bl\BlCargaSISESAT.vbproj
      target_project: bl\BlCargaSISESAT.vbproj
      receiver_path: null
      method: DescomprimirArchivo
      target: Sonda.Gestion.Nssmut.Bl.BlCargaSISESAT.blPistCargaArchSisesat.descomprimirarchivo
    - status: CORRECT
      evidence: webADHAdmCalculoDs67\ucADHGenArcServicePDF.ascx.vb:74
      source_project: WebADHAdmCalculoDs67.vbproj
      target_project: WebADHAdmCalculoDs67.vbproj
      receiver_path: null
      method: Mostrar_Campos
      target: Sonda.Gestion.Nssmut.Web.ADHAdmCalculoDs67.ucADHGenArcServicePDF.mostrar_campos
    - status: CORRECT
      evidence: webADHAdmCalculoDs67\ucADHGenArcServicePDF.ascx.vb:102
      source_project: WebADHAdmCalculoDs67.vbproj
      target_project: WebADHAdmCalculoDs67.vbproj
      receiver_path: null
      method: Grabar_Lote
      target: Sonda.Gestion.Nssmut.Web.ADHAdmCalculoDs67.ucADHGenArcServicePDF.grabar_lote
    - status: CORRECT
      evidence: webADHAdmCalculoDs67\ucADHGenArcServicePDF.ascx.vb:142
      source_project: WebADHAdmCalculoDs67.vbproj
      target_project: WebADHAdmCalculoDs67.vbproj
      receiver_path: null
      method: Mostrar_Campos
      target: Sonda.Gestion.Nssmut.Web.ADHAdmCalculoDs67.ucADHGenArcServicePDF.mostrar_campos
    - status: CORRECT
      evidence: webADHAdmCalculoDs67\ucADHGenArcServicePDF.ascx.vb:149
      source_project: WebADHAdmCalculoDs67.vbproj
      target_project: WebADHAdmCalculoDs67.vbproj
      receiver_path: null
      method: Mostrar_Campos
      target: Sonda.Gestion.Nssmut.Web.ADHAdmCalculoDs67.ucADHGenArcServicePDF.mostrar_campos
    - status: CORRECT
      evidence: webADHAdmCalculoDs67\ucADHMO820_DTA.ascx.vb:138
      source_project: WebADHAdmCalculoDs67.vbproj
      target_project: WebADHAdmCalculoDs67.vbproj
      receiver_path: null
      method: Valida_Folio_Contrato
      target: Sonda.Gestion.Nssmut.Web.ADHAdmCalculoDs67.ucADHMO820_DTA.valida_folio_contrato
    - status: CORRECT
      evidence: webADHAdmCalculoDs67\ucADHMO820_DTA.ascx.vb:485
      source_project: WebADHAdmCalculoDs67.vbproj
      target_project: WebADHAdmCalculoDs67.vbproj
      receiver_path: null
      method: Valida_Folio_Contrato
      target: Sonda.Gestion.Nssmut.Web.ADHAdmCalculoDs67.ucADHMO820_DTA.valida_folio_contrato
    - status: CORRECT
      evidence: webADHAdmCalculoDs67\ucADHMO822_DGI.ascx.vb:167
      source_project: WebADHAdmCalculoDs67.vbproj
      target_project: WebADHAdmCalculoDs67.vbproj
      receiver_path: null
      method: Valida_Folio_Contrato
      target: Sonda.Gestion.Nssmut.Web.ADHAdmCalculoDs67.ucADHMO822_DGI.valida_folio_contrato

INFERRED_SAMPLE:
  total_inferred_R1_1: 0
  classification:
    REASONABLE: 0
    SHOULD_CONFIRM: 0
    SHOULD_UNRESOLVE: 0
    INCORRECT: 0
  assessment: PASS
  notes:
    - weak fabricated local targets are gone.
    - previous examples such as PREComite.isnothing, ucADHActualizaTasas.format and JavaScript string functions no longer appear as inferred calls.

UNRESOLVED_CAUSES:
  total_unresolved_R1_1: 217580
  grouped_main_causes:
    external_or_framework_receiver:
      examples:
        - PREComite.vb:11 dbc.BeginTrans()
        - PREComite.vb:14 dbc.ExecProc(...)
        - PREComite.vb:20 dbc.Commit()
        - PREComite.vb:25 dbc.Close()
      assessment: healthy_conservatism_for_R1_1
    array_declaration_or_values_noise:
      examples:
        - PREComite.vb:13 values()
        - PREComite.vb:34 values()
        - bl\blPistCargaArchSisesat.vb:33 values()
      assessment: residual_noise_non_blocking
      note: no confirmed/inferred false target is created; future cleanup recommended.
    unresolved_control_or_component_receiver:
      examples:
        - ucADHBusEmpresa.ascx.vb:113 tpaBusEmpresa.ColumnaPorId(...)
        - webADHContratos2\ucADHBUPerNomCom.ascx.vb:93 Me.tpaBusPersona.ColumnaPorId(...)
      assessment: expected_until_WebForms_event/control_mapping
    initialize_component_unresolved:
      examples:
        - CabeceraGrande.ascx.vb:14 InitializeComponent()
      assessment: acceptable_conservatism
    multiple_candidates:
      R1: 8808
      R1_1: 4852
      assessment: improved
  overall_assessment: unresolved growth is healthy conservatism, not material regression.

CROSS_PROJECT_CHECK:
  total_confirmed_cross_project_R1: 7841
  total_confirmed_cross_project_R1_1: 9293
  structural_reference_supported_R1_1: 4956
  assessment: PASS
  note: not all coherent fully-qualified calls have direct ProjectReference evidence in V1 indexes; unsupported cases should remain reviewable by source/target project fields.
  validated_samples:
    - status: CORRECT
      source_project: WebADHAdmCalculoDs67.vbproj
      target_project: bl\blADHAdmCalculoDs67\blADHAdmCalculoDs67.vbproj
      evidence: webADHAdmCalculoDs67\ucADHActualizaTasas.ascx.vb:61
      receiver_path: Bl.ADHAdmCalculoDs67.blADHds67
      method: txtraerPereva
      structural_ref: true
    - status: CORRECT
      source_project: WebADHAdmCalculoDs67.vbproj
      target_project: bl\blADHAdmCalculoDs67\blADHAdmCalculoDs67.vbproj
      evidence: webADHAdmCalculoDs67\ucADHActualizaTasas.ascx.vb:124
      receiver_path: Bl.ADHAdmCalculoDs67.blADHds67
      method: txTraerDatosRut
      structural_ref: true
    - status: CORRECT
      source_project: WebADHAdmCalculoDs67.vbproj
      target_project: bl\blADHAdmCalculoDs67\blADHAdmCalculoDs67.vbproj
      evidence: webADHAdmCalculoDs67\ucADHAnexoDEU.ascx.vb:58
      receiver_path: Bl.ADHAdmCalculoDs67.blUtil
      method: CargaCamposFormulario
      structural_ref: true
    - status: CORRECT
      source_project: WebADHAdmCalculoDs67.vbproj
      target_project: bl\blADHAdmCalculoDs67\blADHAdmCalculoDs67.vbproj
      evidence: webADHAdmCalculoDs67\ucADHCargaTasaHistorica.ascx.vb:276
      receiver_path: Bl.ADHAdmCalculoDs67.blPadhD67Rut
      method: txCargarAdhTasas
      structural_ref: true
    - status: CORRECT
      source_project: WebADHAdmCalculoDs67.vbproj
      target_project: bl\blADHAdmCalculoDs67\blADHAdmCalculoDs67.vbproj
      evidence: webADHAdmCalculoDs67\ucADHCargaTasaHistorica.ascx.vb:331
      receiver_path: Bl.ADHAdmCalculoDs67.blPadhD67Rut
      method: txReversarAdhTasas
      structural_ref: true
    - status: CORRECT
      source_project: WebADHAdmCalculoDs67.vbproj
      target_project: bl\blParGenerales\blParGenerales.vbproj
      evidence: webADHAdmCalculoDs67\ucADHCargaTasaHistorica.ascx.vb:90
      receiver_path: Bl.ParametrosGenerales.ParRuta
      method: txtraer
      structural_ref: false
      note: fully-qualified receiver is coherent; direct ProjectReference was not found in V1 structural edge set.
    - status: CORRECT
      source_project: WebADHAdmCalculoDs67.vbproj
      target_project: bl\blParGenerales\blParGenerales.vbproj
      evidence: webADHAdmCalculoDs67\ucADHCartasDefine.ascx.vb:111
      receiver_path: Bl.ParametrosGenerales.ParNum
      method: txLlenarDropDownList
      structural_ref: false
    - status: CORRECT
      source_project: bl\BlCargaSISESAT.vbproj
      target_project: bl\blParGenerales\blParGenerales.vbproj
      evidence: bl\blPistCargaArchSisesat.vb:223
      receiver_path: Bl.ParametrosGenerales.ParRuta
      method: txtraer
      structural_ref: false
    - status: CORRECT
      source_project: WebADHAdmCalculoDs67.vbproj
      target_project: bl\blADHAdmCalculoDs67\blADHAdmCalculoDs67.vbproj
      evidence: webADHAdmCalculoDs67\ucADHCartasFirmas2.ascx.vb:50
      receiver_path: Bl.ADHAdmCalculoDs67.blPadhD67Zonales
      method: txLeePeriodos
      structural_ref: true
    - status: CORRECT
      source_project: WebADHAdmCalculoDs67.vbproj
      target_project: bl\blADHAdmCalculoDs67\blADHAdmCalculoDs67.vbproj
      evidence: webADHAdmCalculoDs67\ucADHCartasFolio.ascx.vb:64
      receiver_path: Bl.ADHAdmCalculoDs67.blADHds67
      method: txleeInfRutEmpresa
      structural_ref: true

DEDUP_CHECK:
  R1:
    functional_dependencies_total: 532200
    duplicate_logical_dependency_keys: 56114
    duplicate_extra_rows: 290389
    edges_with_evidence_count_gt1: 0
  R1_1:
    functional_dependencies_total: 193593
    duplicate_logical_dependency_keys: 0
    duplicate_extra_rows: 0
    edges_with_evidence_count_gt1: 23488
    logical_evidence_total: 308981
  evidence_preservation:
    status: PASS
    examples:
      - relation: Class -> UsesClass
        source: PREComite
        target: OraConn
        evidence_count: 4
        evidence_samples:
          - dbc = New OraConn()
      - relation: Class -> UsesClass
        source: PREComite
        target: SondaExceptionManager
        evidence_count: 4
        evidence_samples:
          - Dim sm As New SondaExceptionManager(e, False)

ERRORS:
  R1_errors: 0
  R1_1_errors: 0
  status: PASS
  regression: false

REQUIRED_FIXES:
  CRITICAL: []
  HIGH: []
  MEDIUM:
    - optional_future_cleanup: filter array declarations such as values() from unresolved calls.
    - optional_future_classification: classify unresolved framework/external calls separately from unresolved application calls.
    - optional_future_validation: enrich cross-project confidence with explicit ProjectReference/DLL evidence when available.
  LOW:
    - preserve original method casing in resolved_target while keeping normalized lookup keys.

DECISION: A) V2-R1_1_APROBADA_PARA_R2
