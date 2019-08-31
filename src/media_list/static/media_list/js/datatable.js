class DataTableView {
  constructor($element) {
    this.table = $element.DataTable(this.dataTableOptions());
    this.bindEvents();
  }

  bindEvents() {
    $('#list-filter-by-title').keyup((event) => {
      this.table.column('title:name').search(event.target.value).draw();
    });
    $('#list-filter-by-source').change((event) => {
      this.table.column('source:name').search(event.target.value).draw();
    });
    $('#list-filter-by-completed').change((event) => {
      console.log(event.target.value);
      this.table.column('completed:name').search(event.target.value).draw();
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
        name: 'volumes',
        orderable: true,
        searchable: false,
      },
      {
        name: 'completed',
        orderable: false,
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
