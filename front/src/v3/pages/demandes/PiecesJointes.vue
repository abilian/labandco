<template>
  <ul>
    <li class="row">
      <div class="col-md-6">
        <a href="/demandes/2643/pj/8209"
          >Sorbonne_Univ-FVE-SNCF-EI__Chaire_Industrielle_Silversight_II__version_finale_.docx</a
        >

        <br />(déposée par: Zahoua Djallali). Le 03/04/2019 a 17:09.
      </div>
      <div class="col-md-1">
        <form
          method="post"
          enctype="multipart/form-data"
          role="form"
          name="delete-attachment"
          class="form-inline"
          action="/demandes/2643/pj/8209/delete"
        >
          <button type="submit" class="form-group form-actions text-danger">
            <span class="glyphicon glyphicon-trash"></span>
          </button>
        </form>
      </div>
    </li>
  </ul>
</template>

<script>
export default {
  props: { demande: Object },
};
</script>
