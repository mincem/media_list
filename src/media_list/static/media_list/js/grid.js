$(document).ready(function () {
  document.detailView = new DetailView();
  $('.media-grid-item').click(renderDetailView);
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
