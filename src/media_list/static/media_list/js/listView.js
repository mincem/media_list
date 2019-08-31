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
    $('#list-filter-by-title-clear').click(() => {
      $('#list-filter-by-title').val('').focus();
      this.applyFilters();
    })
  }
}

function TitleListFilter() {
  this.element = '#list-filter-by-title';
  this.action = 'keyup';
  this.apply = function ($list) {
    // let searchInput = $(this.element).val().toLowerCase();
    // $list.find('tr').filter(function () {
    //   $(this).toggle($(this).find('.ml-cell-title').text().toLowerCase().indexOf(searchInput) > -1)
    // });
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
