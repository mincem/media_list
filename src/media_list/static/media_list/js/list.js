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

function TitleListFilter() {
  this.element = '#list-filter-by-title';
  this.action = 'keyup';
  this.apply = function ($list) {
    let searchInput = $(this.element).val().toLowerCase();
    $list.find('tr').filter(function () {
      $(this).toggle($(this).find('.ml-cell-title').text().toLowerCase().indexOf(searchInput) > -1)
    });
  }
}

function SourceListFilter() {
  this.element = '#list-filter-by-source';
  this.action = 'change';
  this.apply = function ($list) {
    let selectedSource = $(this.element).val();
    if (!selectedSource) {
      $list.find('tr').show();
      return;
    }
    $list.find('tr').hide();
    $list.find(`tr[data-source="${selectedSource}"]`).show();
  }
}

class ListView {
  constructor() {
    this.$list = $('#media-list').find('tbody');
    this.filters = [
      new TitleListFilter(),
      new SourceListFilter()
    ];
  }

  render() {
    let i;
    for (i = 0; i < this.filters.length; i++) {
      const filter = this.filters[i];
      $(filter.element).on(filter.action, () => {
        filter.apply(this.$list);
      });
    }
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
