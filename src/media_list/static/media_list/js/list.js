$(document).ready(function () {
  document.detailView = new DetailView();

  $('.ml-row').click(renderDetailView);

  $("#filters").find('.filter-title').on('keyup', filterListByTitle);
});

function renderDetailView() {
  let series = new MediaSeries($(this).data('series-id'));
  document.detailView.register(series);
  document.detailView.render();
}

function filterListByTitle(event) {
  let searchInput = $(event.target).val().toLowerCase();
  $('#media-list').find('tbody').find('tr').filter(function () {
    $(this).toggle($(this).find('.ml-cell-title').text().toLowerCase().indexOf(searchInput) > -1)
  });
}

class MediaSeries {
  constructor(id) {
    this.id = id;
  }
}

class DetailView {
  constructor() {
    this.mediaSeries = null;
    this.$modal = $('#details-modal');
  }

  register(mediaSeries) {
    this.mediaSeries = mediaSeries;
  }

  render() {
    if (this.mediaSeries === null) return;
    $.ajax({
      url: `/media_list/detail/${this.mediaSeries.id}/`,
      type: 'get',
      dataType: 'html',
      success: (htmlData) => {
        this.display(htmlData)
      }
    });
  }

  fooBeginLoading() {
    this.$modal.find('#details-modal-loading').removeClass('hidden');
  }

  fooEndLoading() {
    this.$modal.removeClass('spinner-border');
    this.$modal.find('#details-modal-loading').addClass('hidden');
  }

  display(htmlData) {
    this.$modal.find('.modal-content').html(htmlData);
    this.$modal.modal('show');
    $('#action-find-baka-id').click(() => {
      this.findBakaID()
    });
    $('#action-get-baka-data').click(() => {
      this.getBakaData()
    });
  }

  findBakaID() {
    this.fooBeginLoading();
    $.ajax({
      url: `/media_list/get_baka_id/${this.mediaSeries.id}/`,
      type: 'get',
      dataType: 'html',
      success: (htmlData) => {
        this.display(htmlData);
      }
    });
    this.fooEndLoading();
  }

  getBakaData() {
    this.fooBeginLoading();
    $.ajax({
      url: `/media_list/get_baka_info/${this.mediaSeries.id}/`,
      type: 'get',
      dataType: 'html',
      success: (htmlData) => {
        this.display(htmlData);
      }
    });
    this.fooEndLoading();
  }
}
