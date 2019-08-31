$(document).ready(function () {
  document.listView = new ListView();
  document.listView.render();

  document.detailView = new DetailView();

  $('.ml-row').click(renderDetailView);
});

function renderDetailView(id) {
  let series_id = Number.isInteger(id) ? id : $(this).data('series-id');
  let series = new MediaSeries(series_id);
  document.detailView.register(series);
  document.detailView.render();
}

class MediaSeries {
  constructor(id) {
    this.id = id;
  }
}
