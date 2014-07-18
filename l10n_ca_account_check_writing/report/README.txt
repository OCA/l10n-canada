The third table in the report has to be on the third part of the page.
We can fix height of the check by adding empty rows in the SXW file,
but we can not fix the 2nd tables's height.

The way to do it, after converting the SXW file to RML, is adding
is adding a rowHeights attribute for the second table :

    <blockTable rowHeights="80.0mm" colWidths="591.0" style="Table2">


The amount line need to be in Courier font 9.
    <paraStyle name="P17" fontName="Courier" fontSize="9.0" leading="11" alignment="LEFT"/>

Add space between check and stubs, before <blockTable rowHeights="80.0mm"  colWidths="591.0" style="Table2">
    <spacer length="1cm"/>