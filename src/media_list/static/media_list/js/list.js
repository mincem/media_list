$(document).ready(function () {
  // document.listView = new ListView();
  // document.listView.render();
  document.detailView = new DetailView();
  document.dataTableView = new DataTableView(
    $('#media-list-table'),
    dataTableColumns,
    filterEvents
  );

  $('.ml-row').click(renderDetailView);
});

function renderDetailView(id, viewURL) {
  let series_id = Number.isInteger(id) ? id : $(this).data('series-id');
  let series = new MediaSeries(series_id);
  let url = viewURL || this.dataset.url;
  document.detailView.register(series, url);
  document.detailView.render();
}

class MediaSeries {
  constructor(id) {
    this.id = id;
  }
}
