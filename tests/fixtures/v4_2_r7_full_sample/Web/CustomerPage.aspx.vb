Public Class CustomerPage
    Inherits System.Web.UI.Page

    Protected Sub Page_Load(ByVal sender As Object, ByVal e As System.EventArgs) Handles Me.Load
        SetFocus(Me.txtCustomerId)
    End Sub

    Protected Sub btnSave_Click(sender As Object, e As EventArgs)
        Dim service As New CustomerService()
        service.Save()
    End Sub

    Protected Sub btnNotify_Click(sender As Object, e As EventArgs)
        ExternalMailer.Send("customer updated")
    End Sub
End Class
