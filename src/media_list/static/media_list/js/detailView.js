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
    let $loadingAnimation = $button.clone();
    $loadingAnimation
      .attr('disabled', 'disabled')
      .addClass('loading-button')
      .html('<div class="spinner-border" role="status"></div>');
    $button.after($loadingAnimation).hide();
  }

  hideLoadingAnimation($button) {
    $button
      .show()
      .siblings('.loading-button').remove();
  }

  display(htmlData) {
    this.$modal.find('.modal-content').html(htmlData);
    this.$modal.modal('show');
    this.displayInterestForm();
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

  displayInterestForm() {
    let $interestForm = this.$modal.find('.media-interest-form');
    new RangeField($interestForm);
    $interestForm.submit((event) => {
      this.updateInterest(event)
    });
  }

  findBakaID() {
    const $button = $('#action-find-baka-id');
    this.showLoadingAnimation($button);
    $.ajax({
      url: `/media_list/get_baka_id/${this.mediaSeries.id}/`,
      type: 'get',
      dataType: 'html',
      success: (htmlData) => {
        this.display(htmlData);
      },
      error: () => {
        this.hideLoadingAnimation($button);
        alert("Error finding ID!");
      }
    });
  }

  getBakaData() {
    const $button = $('#action-get-baka-data');
    this.showLoadingAnimation($button);
    $.ajax({
      url: `/media_list/get_baka_info/${this.mediaSeries.id}/`,
      type: 'get',
      dataType: 'html',
      success: (htmlData) => {
        this.display(htmlData);
      },
      error: () => {
        this.hideLoadingAnimation($button);
        alert("Error retrieving data!");
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

  updateInterest(event) {
    event.preventDefault();
    let $form = $(event.target);
    $.ajax({
      url: `/media_list/edit_interest/${this.mediaSeries.id}/`,
      type: 'post',
      dataType: 'html',
      data: $form.serializeArray().concat([{
        name: 'csrfmiddlewaretoken',
        value: getCookie('csrftoken')
      }]),
      success: (htmlData) => {
        this.display(htmlData);
      }
    });
  }
}
