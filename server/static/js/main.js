const serverUrl = '//localhost:8080/';

// const serverUrl = '//92.53.91.203:8080/';

function showImage(image_url) {
    $("#image-container").html("<img class='image' src=" + image_url + ">")
}

function getImageByTag() {
    tag = $("#tagInput").val();

    if (!tag) {
        toastr.error('Empty tag value');
        return;
    }

    $("#get-image-button").attr("disabled", true);
    $("#image-container").html();

    $.ajax({
        url: serverUrl + "get_image?tag=" + tag,
        type: "GET"
    })
        .done(function (data) {
            $("#get-image-button").attr("disabled", false);
            image_url = data["image_url"];
            showImage(image_url);
        })
        .fail(function (error) {
            responseText = JSON.parse(error['responseText']);
            errorMsg = responseText["error_msg"];

            toastr.error('Error: ' + errorMsg);
            $("#get-image-button").attr("disabled", false);
        });
}

$(document).ready(function () {
    $("#get-image-button").bind("click", function () {
        getImageByTag();
    });
});