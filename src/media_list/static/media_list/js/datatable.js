$(document).ready(function () {
  $('#media-list-table').DataTable(dataTableOptions);
});

dataTableOptions = {
  'columns': [
    {'name': 'image', 'orderable': false},
    {'name': 'source', 'orderable': false},
    {'name': 'title', 'orderable': true},
    {'name': 'volumes', 'orderable': true},
    {'name': 'completed', 'orderable': false},
    {'name': 'interest', 'orderable': true},
    {'name': 'status', 'orderable': true},
    {'name': 'actions', 'orderable': false}
  ],
  'order': [[2, 'asc']],
  'paging': false,
  'scrollY': '70vh',
  'scrollCollapse': true,
};
