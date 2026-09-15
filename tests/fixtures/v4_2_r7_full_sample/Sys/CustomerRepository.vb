Public Class CustomerRepository
    Public Sub Save()
        Dim conn As New OracleConnection()
        Dim cmd As New OracleCommand("PKG_CUSTOMER.SAVE_CUSTOMER", conn)
        cmd.CommandType = CommandType.StoredProcedure
        cmd.ExecuteNonQuery()
    End Sub
End Class
