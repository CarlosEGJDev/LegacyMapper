Public Class CustomerService
    Public Sub Save()
        Dim repo As New CustomerRepository()
        repo.Save()
    End Sub
End Class
