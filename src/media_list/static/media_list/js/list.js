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
    if (!selectedSource) return;
    $list.find(`tr[data-source!="${selectedSource}"]`).hide();
  }
}

function CompletedListFilter() {
  this.element = '#list-filter-by-completed';
  this.action = 'change';
  this.apply = function ($list) {
    let selectedState = $('input[name=filter-by-completed]:checked', this.element).val();
    if (!selectedState) return;
    $list.find(`tr[data-completed!="${selectedState}"]`).hide();
  }
}

function BakaInfoListFilter() {
  this.element = '#list-filter-by-baka-info';
  this.action = 'change';
  this.apply = function ($list) {
    let selectedState = $('input[name=filter-by-baka-info]:checked', this.element).val();
    if (!selectedState) return;
    $list.find(`tr[data-baka-info!="${selectedState}"]`).hide();
  }
}

class ListView {
  constructor() {
    this.$list = $('#media-list').find('tbody');
    this.filters = [
      new TitleListFilter(),
      new SourceListFilter(),
      new CompletedListFilter(),
      new BakaInfoListFilter(),
    ];
  }

  render() {
    this.applyFilters();
    this.bindFilterEvents();
  }

  applyFilters() {
    this.$list.find('tr').show();
    for (let i = 0; i < this.filters.length; i++) this.filters[i].apply(this.$list);
  }

  bindFilterEvents() {
    for (let i = 0; i < this.filters.length; i++) {
      const filter = this.filters[i];
      $(filter.element).on(filter.action, () => {
        this.applyFilters();
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

  showLoadingAnimation($button) {
    $button
      .attr('disabled','disabled')
      .html('<div class="spinner-border" role="status"></div>');
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
    $('#action-swap-titles').click(() => {
      this.swapTitles()
    });
  }

  findBakaID() {
    this.showLoadingAnimation($('#action-find-baka-id'));
    $.ajax({
      url: `/media_list/get_baka_id/${this.mediaSeries.id}/`,
      type: 'get',
      dataType: 'html',
      success: (htmlData) => {
        this.display(htmlData);
      }
    });
  }

  getBakaData() {
    this.showLoadingAnimation($('#action-get-baka-data'));
    $.ajax({
      url: `/media_list/get_baka_info/${this.mediaSeries.id}/`,
      type: 'get',
      dataType: 'html',
      success: (htmlData) => {
        this.display(htmlData);
      }
    });
  }

  swapTitles() {
    $.ajax({
      url: `/media_list/swap_titles/${this.mediaSeries.id}/`,
      type: 'get',
      dataType: 'html',
      success: (htmlData) => {
        this.display(htmlData);
      }
    });
  }
}
