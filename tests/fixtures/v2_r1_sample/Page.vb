Imports Empresa.Sample

Public Class Page
    Public Sub Run()
        Dim servicio As New Servicio()
        servicio.Procesar()
        Servicio.SharedProcesar()
        Local()
    End Sub

    Public Sub Local()
    End Sub
End Class
