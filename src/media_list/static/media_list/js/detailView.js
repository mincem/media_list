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
      .attr('disabled', 'disabled')
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
