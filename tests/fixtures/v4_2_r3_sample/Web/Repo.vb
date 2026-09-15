Public Class Repo
    Public Sub Save()
        Dim conn As New OracleConnection()
        Dim cmd As New OracleCommand("PKG.SAVE", conn)
        cmd.CommandType = CommandType.StoredProcedure
        cmd.ExecuteNonQuery()
    End Sub
End Class
