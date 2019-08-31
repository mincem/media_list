$(document).ready(function () {
  let table = $('#media-list-table').DataTable(dataTableOptions);

  $('#list-filter-by-title').on('keyup', function () {
    table.search(this.value).draw();
  });
});

let dataTableColumns = [
  {
    name: 'image',
    orderable: false,
    searchable: false,
  },
  {
    name: 'source',
    orderable: false,
    searchable: false,
  },
  {
    name: 'title',
    orderable: true,
    searchable: true,
  },
  {
    name: 'volumes',
    orderable: true,
    searchable: false,
  },
  {
    name: 'completed',
    orderable: false,
    searchable: false,
  },
  {
    name: 'interest',
    orderable: true,
    searchable: false
  },
  {
    name: 'status',
    orderable: true,
    searchable: false,
  },
  {
    name: 'actions',
    orderable: false,
    searchable: false,
  }
];

let dataTableOptions = {
  columns: dataTableColumns,
  order: [[2, 'asc']],
  paging: false,
  scrollY: '72vh',
  scrollCollapse: true,
  sDom: 'ltipr', // Everything except search box
};
