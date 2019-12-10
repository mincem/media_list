class DetailView {
  constructor() {
    this.mediaSeries = null;
    this.viewURL = null;
    this.$modal = $('#details-modal');
  }

  register(mediaSeries, viewURL) {
    this.mediaSeries = mediaSeries;
    this.viewURL = viewURL;
  }

  render() {
    if (!this.mediaSeries || !this.viewURL) return;
    $.ajax({
      url: this.viewURL,
      type: 'get',
      dataType: 'html',
      success: (htmlData) => {
        this.display(htmlData);
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
    $('#action-find-baka-id').click((event) => {
      this.findBakaID(event);
    });
    $('#action-get-baka-data').click((event) => {
      this.getBakaData(event);
    });
    $('#action-swap-titles').click((event) => {
      this.swapTitles(event);
    });
  }

  displayInterestForm() {
    let $interestForm = this.$modal.find('.media-interest-form');
    new RangeField($interestForm);
    $interestForm.submit((event) => {
      this.updateInterest(event);
    });
  }

  findBakaID(event) {
    const $button = $('#action-find-baka-id');
    this.showLoadingAnimation($button);
    $.ajax({
      url: event.currentTarget.dataset.url,
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

  getBakaData(event) {
    const $button = $('#action-get-baka-data');
    this.showLoadingAnimation($button);
    $.ajax({
      url: event.currentTarget.dataset.url,
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

  swapTitles(event) {
    $.ajax({
      url: event.currentTarget.dataset.url,
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
      url: event.target.dataset.url,
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
