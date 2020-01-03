let bindFilterByTitle = function (table) {
  $('#list-filter-by-title').keyup((event) => {
    table.column('title:name').search(event.target.value).draw();
  });
  $('#list-filter-by-title-clear').click(() => {
    $('#list-filter-by-title').val('').focus();
    table.column('title:name').search('').draw();
  });
};

let bindFilterByStaff = function (table) {
  $('#list-filter-by-staff').keyup((event) => {
    table.column('staff:name').search(event.target.value).draw();
  });
  $('#list-filter-by-staff-clear').click(() => {
    $('#list-filter-by-staff').val('').focus();
    table.column('staff:name').search('').draw();
  });
};

let bindFilterBySource = function (table) {
  $('#list-filter-by-source').change((event) => {
    table.column('source:name').search(event.target.value).draw();
  });
};

let bindFilterByCompleted = function (table) {
  $('#list-filter-by-completed').change((event) => {
    table.column('volumes:name').search(event.target.value).draw();
  });
};

let bindFilterByBakaInfo = function (table) {
  $('#list-filter-by-baka-info').change((event) => {
    let searchValue;
    if (event.target.value === 'True') searchValue = '\S';
    else if (event.target.value === 'False') searchValue = '^$';
    else searchValue = '';
    table.column('staff:name').search(searchValue, true).draw();
  });
};

const filterEvents = [
  bindFilterByTitle,
  bindFilterByStaff,
  bindFilterBySource,
  bindFilterByCompleted,
  bindFilterByBakaInfo,
];

const dataTableColumns = [
  {
    name: 'image',
    orderable: false,
    searchable: false,
    width: '10px',
  },
  {
    name: 'source',
    orderable: false,
    searchable: true,
    width: '10px',
  },
  {
    name: 'title',
    orderable: true,
    searchable: true,
  },
  {
    name: 'staff',
    orderable: true,
    searchable: true,
  },
  {
    name: 'year',
    orderable: true,
    searchable: false,
    width: '10px',
  },
  {
    name: 'volumes',
    orderable: true,
    searchable: true,
  },
  {
    name: 'interest',
    orderable: true,
    searchable: false,
    width: '10px',
  },
  {
    name: 'status',
    orderable: true,
    searchable: false,
    width: '10px',
  },
  {
    name: 'actions',
    orderable: false,
    searchable: false,
    width: '10px',
  }
];
