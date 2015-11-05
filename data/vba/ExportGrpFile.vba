Attribute VB_Name = "ExportGrpFile"
Sub reg()
Attribute reg.VB_ProcData.VB_Invoke_Func = "r\n14"
'
' reg Makro
'
' Tastenkombination: Strg+r
'
' Let you want to analize a sequence that you have just enter in the big alignment.
' You have allready inserted a row in the big table with the correct name (the same als in MEGA)
' and with the position of biggining and end of the sequence in the alignment.
' You now need to set the region and export the column into a group file.
' With this macro you just click on the sequences row and then press Ctrl-r.
' First create the directory Aut.MEGA\

    Application.CutCopyMode = False
    Dim beg As Integer, fin As Integer, FileName As String
     
    beg = Application.Intersect(Selection, Range("SeqBeg")).Value ' where beging
    fin = Application.Intersect(Selection, Range("SeqEnd")).Value ' where end the seq
    Range("manual_beg").Value = beg    ' set as the manually selected region
    Range("manual_end").Value = fin
    Range("GenRegSelect").Value = 3    ' select the manually selected region in the big table
                                       ' this generate the column with the "span" or "out"
    Range("span_column").Copy
    
    
    FileName = Application.ActiveWorkbook.Path & "\HEV." & Str(beg) & "-" & Str(fin) & ".grp.txt"

    With Workbooks.Add   ' create a new workbook file
      .Sheets(1).Range("A1").PasteSpecial Paste:=xlPasteValues, Operation:=xlNone, SkipBlanks:=False, Transpose:=False
      .SaveAs FileName:=FileName, FileFormat:=xlTextMSDOS
      .Close SaveChanges:=False
    End With
    
    MsgBox ("A file " & FileName & " have been created.")
      
End Sub

