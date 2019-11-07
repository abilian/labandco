<template>
  <div class="row">
    <div class="col-md-9 col-sm-6 col-xs-12">
      <div class="info-box box-message-dgrtt">
        <span class="info-box-icon bg-teal"
          ><i class="far fa-info-circle"></i
        ></span>

        <div class="info-box-content message-dgrtt">
          <div v-html="messageDgrtt"></div>
        </div>
      </div>
    </div>

    <div class="col-md-3 col-sm-6 col-xs-12">
      <!--      <a href="{{ url_for(" main.contacts") }}">-->
      <a href="#">
        <div class="info-box">
          <span class="info-box-icon bg-teal"
            ><i class="far fa-users"></i
          ></span>

          <div class="info-box-content">
            <span class="info-box-text">Mes contacts</span>
          </div>
        </div>
      </a>
    </div>
  </div>
</template>

<script>
export default {
  name: "MessageDgrtt",

  data() {
    return {
      messageDgrtt: "Test <b>html</b>",
    };
  },
};
</script>

<style scoped></style>
