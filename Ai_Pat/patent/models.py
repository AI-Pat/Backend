from django.db import models

class Patent(models.Model):
    patent_id = models.CharField(max_length=255, primary_key=True)
    patent_cntry_cd = models.CharField(max_length=255)
    patent_keyword_val = models.CharField(max_length=255)
    patent_nm = models.CharField(max_length=255)
    patent_kor_nm = models.CharField(max_length=255)
    patent_applcnt_nm = models.CharField(max_length=255)
    patent_applcnt_kor_nm = models.CharField(max_length=255)
    patent_applcnt_cntry_cd = models.CharField(max_length=255)
    patent_og_text_file_nm = models.CharField(max_length=255)
    patent_og_text_file_extnsn_nm = models.CharField(max_length=255)
    patent_create_dt = models.DateField()

    def __str__(self):
        return self.patent_nm

class AttachFile(models.Model):
    file_nm = models.CharField(max_length=255)
    file_extnsn_nm = models.CharField(max_length=255)
    file_size_val = models.IntegerField()
    file_size_unit_nm = models.CharField(max_length=255)
    file_ver_val = models.IntegerField()
    file_upload_user_id = models.CharField(max_length=255)
    file_loc_val = models.CharField(max_length=255)
    create_user_id = models.CharField(max_length=255)
    create_dtm = models.DateTimeField()
    modify_user_id = models.CharField(max_length=255)
    modify_dtm = models.DateTimeField()
    patent = models.OneToOneField(Patent, on_delete=models.CASCADE, null=True, blank=True, related_name='attach_file')

    class Meta:
        unique_together = ('file_nm', 'file_extnsn_nm')

    def __str__(self):
        return self.file_nm