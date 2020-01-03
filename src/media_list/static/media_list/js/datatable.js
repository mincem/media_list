class DataTableView {
  constructor($element, columns, eventBindings) {
    this.dataTableColumns = columns;
    this.table = $element.DataTable(this.dataTableOptions());
    this.bindEvents(eventBindings);
  }

  bindEvents(eventBindings) {
    for (let i = 0; i < eventBindings.length; i++) {
      this.eventBindings[i](this.table);
    }
  }

  dataTableOptions() {
    return {
      columns: this.dataTableColumns,
      order: [[2, 'asc']],
      paging: false,
      scrollY: '72vh',
      scrollCollapse: true,
      sDom: 'ltipr', // Everything except search box
    };
  }
}
