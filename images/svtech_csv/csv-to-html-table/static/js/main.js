function format_link(link){
  if (link)
    return "<a href='" + link + "' target='_blank'>" + link + "</a>";
  else
    return "";
}
var path = document.getElementById("csv_path").dataset.path;
CsvToHtmlTable.init({
  csv_path: path,
  element: 'table-container',
  allow_download: true,
  csv_options: {separator: ',', delimiter: '"'},
  datatables_options: {"paging": true},
  // custom_formatting: [[4, format_link]]
});