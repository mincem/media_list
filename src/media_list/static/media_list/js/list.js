$(document).ready(function () {
  document.listView = new ListView();
  document.listView.render();

  document.detailView = new DetailView();

  $('.ml-row').click(renderDetailView);
});

function renderDetailView() {
  let series = new MediaSeries($(this).data('series-id'));
  document.detailView.register(series);
  document.detailView.render();
}

class MediaSeries {
  constructor(id) {
    this.id = id;
  }
}

class ListView {
  constructor() {
    this.$list = $('#media-list').find('tbody');
    this.$filters = $('#filters');
  }

  render() {
    this.$filters.find('.filter-title').on('keyup', (event) => {
      this.filterListByTitle(event);
    });
    this.$filters.find('.filter-source').change((event) => {
      this.filterListBySource(event);
    });
  }

  filterListByTitle(event) {
    let searchInput = $(event.target).val().toLowerCase();
    this.$list.find('tr').filter(function () {
      $(this).toggle($(this).find('.ml-cell-title').text().toLowerCase().indexOf(searchInput) > -1)
    });
  }

  filterListBySource(event) {
    let selectedSource = $(event.target).val();
    if (!selectedSource) {
      this.$list.find('tr').show();
      return;
    }
    this.$list.find('tr').hide();
    this.$list.find(`tr[data-source="${selectedSource}"]`).show();
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
