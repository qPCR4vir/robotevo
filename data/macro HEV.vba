Sub SetRegionAndSaveGrpTxt()
'
' SetRegionAndSaveGrpTxt Makro
'
' Tastenkombination: Strg+r
'
    Application.CutCopyMode = False
    Dim beg As Integer, fin As Integer
    'beg = Range("beg_column").Cells(Selection.Row()).Value
    'fin = Range("end_column").Cells(Selection.Row()).Value
    beg = Application.Intersect(Selection, Range("beg_column")).Value
    fin = Application.Intersect(Selection, Range("end_column")).Value
    Range("manual_beg").Value = beg
    Range("manual_end").Value = fin
    
    Range("span_column").Copy
    Set newtxt = Workbooks.Add
    With newtxt
      Sheets(1).Range("A1").PasteSpecial Paste:=xlPasteValues, Operation:=xlNone, SkipBlanks _
          :=False, Transpose:=False
      .SaveAs Filename:="Aut.MEGA\HEV." & Str(beg) & "-" & Str(fin) & ".grp.txt", FileFormat _
          :=xlTextMSDOS, CreateBackup:=False
      .Close
    End With
      
End Sub


' SetRegionAndSaveGrpTxt Makro
'
' Tastenkombination: Ctrl+r
'
' Let you want to analize a sequence that you have just enter in the big alignment.
' You have allready inserted a row in the big table with the correct name (the same als in MEGA)
' and with the position of biggining and end of the sequence in the alignment.
' You now need to set the region and export the column into a group file.
' With this macro you just click on the sequences row and then press Ctrl-r.

    Application.CutCopyMode = False
    Dim beg As Integer, fin As Integer, FileName As String
     
    beg = Application.Intersect(Selection, Range("SeqBeg")).Value ' where beging
    fin = Application.Intersect(Selection, Range("SeqEnd")).Value ' where end the seq
    Range("manual_beg").Value = beg    ' set as the manually selected region
    Range("manual_end").Value = fin
    Range("GenRegSelect").Value = 3    ' select the manually selected region in the big table
                                       ' this generate the column with the "span" or "out"
    Range("span_column").Copy
    FileName = "Aut.MEGA\HEV." & Str(beg) & "-" & Str(fin) & ".grp.txt"
    ' Set newtxt = Workbooks.Add
    With Workbooks.Add   ' create a new workbook file
      .Sheets(1).Range("A1").PasteSpecial Paste:=xlPasteValues, Operation:=xlNone, SkipBlanks:=False, Transpose:=False
      .SaveAs FileName:=FileName, FileFormat:=xlTextMSDOS, CreateBackup:=False
      .Close
    End With
    
    MessageBox ("A file " & FileName & " have been created.")