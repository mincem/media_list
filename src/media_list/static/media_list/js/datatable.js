class DataTableView {
  constructor($element) {
    this.table = $element.DataTable(this.dataTableOptions());
    this.bindEvents();
  }

  bindEvents() {
    this.bindFilterByTitle();
    this.bindFilterByStaff();
    this.bindFilterBySource();
    this.bindFilterByCompleted();
    this.bindFilterByBakaInfo();
  }

  bindFilterByTitle() {
    $('#list-filter-by-title').keyup((event) => {
      this.table.column('title:name').search(event.target.value).draw();
    });
    $('#list-filter-by-title-clear').click(() => {
      $('#list-filter-by-title').val('').focus();
      this.table.column('title:name').search('').draw();
    });
  }

  bindFilterByStaff() {
    $('#list-filter-by-staff').keyup((event) => {
      this.table.column('staff:name').search(event.target.value).draw();
    });
    $('#list-filter-by-staff-clear').click(() => {
      $('#list-filter-by-staff').val('').focus();
      this.table.column('staff:name').search('').draw();
    });
  }

  bindFilterBySource() {
    $('#list-filter-by-source').change((event) => {
      this.table.column('source:name').search(event.target.value).draw();
    });
  }

  bindFilterByCompleted() {
    $('#list-filter-by-completed').change((event) => {
      this.table.column('volumes:name').search(event.target.value).draw();
    });
  }

  bindFilterByBakaInfo() {
    $('#list-filter-by-baka-info').change((event) => {
      var searchValue;
      if (event.target.value === 'True') searchValue = '\S';
      else if (event.target.value === 'False') searchValue = '^$';
      else searchValue = '';
      this.table.column('staff:name').search(searchValue, true).draw();
    });
  }

  dataTableColumns() {
    return [
      {
        name: 'image',
        orderable: false,
        searchable: false,
      },
      {
        name: 'source',
        orderable: false,
        searchable: true,
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
      },
      {
        name: 'volumes',
        orderable: true,
        searchable: true,
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
  }

  dataTableOptions() {
    return {
      columns: this.dataTableColumns(),
      order: [[2, 'asc']],
      paging: false,
      scrollY: '72vh',
      scrollCollapse: true,
      sDom: 'ltipr', // Everything except search box
    };
  }
}
