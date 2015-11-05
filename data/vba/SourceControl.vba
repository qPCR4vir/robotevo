Attribute VB_Name = "SourceControl"
'   http://stackoverflow.com/questions/131605/best-way-to-do-version-control-for-ms-excel
'   http://www.pretentiousname.com/excel_extractvba/

Option Explicit

Sub CommitToLaptoop()
    CommitVBA ("C:\Prog\HEV\data\vba\")
End Sub

Sub CommitToC()
    CommitVBA ("\\rie-icl01\Homelaufwerk\ariel.rodriguez\Eigene Dokumente\Results\Publica\HEV\HEV\data\vba\")
End Sub

Sub CommitToDrive() 'dont works
    CommitVBA ("C:\Users\Ariel\OneDrive\Documents\Tesis\HEV\data\vba\")
End Sub



Sub CommitVBA(dir As String)

    ' Exports all VBA modules
    Dim i%, sName$

    With ThisWorkbook.VBProject
        For i% = 1 To .VBComponents.Count
            If .VBComponents(i%).CodeModule.CountOfLines > 0 Then
                sName$ = .VBComponents(i%).CodeModule.Name
                sName$ = dir & sName$ & ".vba"
                .VBComponents(i%).Export (sName$)
            End If
        Next i
    End With


End Sub


Sub RevertVBA()

  With ThisWorkbook.VBProject
    For i% = 1 To .VBComponents.Count
        ModuleName = .VBComponents(i%).CodeModule.Name
        .VBComponents.Remove .VBComponents(ModuleName)
        .VBComponents.Import "C:\Prog\HEV\VBA\" & ModuleName & ".vba"
    Next i
  End With

End Sub
