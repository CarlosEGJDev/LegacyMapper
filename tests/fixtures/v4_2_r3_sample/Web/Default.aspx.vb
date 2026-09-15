Public Class CustomerPage
    Inherits System.Web.UI.Page

    Protected Sub btnSave_Click(sender As Object, e As EventArgs)
        Dim repo As New Repo()
        repo.Save()
    End Sub
End Class
