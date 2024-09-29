from django.db import models


class LeadPage(models.Model):
    name = models.CharField('Nazwa LP', max_length=254)

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'marketing_lp_lead_page'
        verbose_name = u'strona'
        verbose_name_plural = u'strony'


class Medium(models.Model):
    name = models.CharField('Nazwa medium', max_length=50)

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'marketing_lp_medium'
        verbose_name = u'medium'
        verbose_name_plural = u'medium'


class Source(models.Model):
    name = models.CharField('Nazwa źródła', max_length=50)

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'marketing_lp_source'
        verbose_name = u'źródło'
        verbose_name_plural = u'źródła'


class PageEntry(models.Model):
    lp = models.ForeignKey(LeadPage, editable=False, db_column='id_lead_page', on_delete=models.CASCADE)
    medium = models.ForeignKey(Medium, db_column='id_medium', verbose_name=u'Medium', null=True, blank=True, editable=False, on_delete=models.CASCADE)
    source = models.ForeignKey(Source, db_column='id_source', verbose_name=u'Źródło', null=True, blank=True, editable=False, on_delete=models.CASCADE)
    # medium = models.CharField(verbose_name=u'Medium', max_length=100, null=True, blank=True, editable=False)
    # source = models.CharField(verbose_name=u'Źródło', max_length=100, null=True, blank=True, editable=False)
    created = models.DateTimeField('Data dodania', auto_now_add=True, editable=False)
    first_name = models.CharField(u'Imię', max_length=254, editable=False, null=True, blank=True)
    last_name = models.CharField('Nazwisko', max_length=254, editable=False, null=True, blank=True)
    client_type = models.CharField('Podmiot', max_length=254, editable=False, null=True, blank=True)
    company_name = models.CharField('Nazwa firmy', max_length=254, editable=False, null=True, blank=True)
    phone = models.CharField('Telefon', max_length=254, editable=False, null=True, blank=True)
    email = models.EmailField('Email', editable=False, null=True, blank=True)
    epi = models.CharField(max_length=255, default='', null=True)
    amount = models.BigIntegerField(verbose_name=u'Kwota pożyczki / Wartość inna', default=0, null=True, blank=True, editable=False)
    office_space = models.BigIntegerField(verbose_name=u'Powierzchnia biura', default=0, null=True, blank=True, editable=False)
    location = models.CharField(u'Lokalizacja biura', max_length=254, null=True, blank=True, editable=False)
    message = models.TextField(verbose_name=u'Wiadomosc', null=True, blank=True, editable=False)
    device = models.CharField(u'Device', max_length=254, editable=False, null=True, blank=True)
    accept1 = models.BooleanField('Zgoda 1 (elektroniczna)', editable=False, default=False)
    accept2 = models.BooleanField('Zgoda 2 (telekomunikacyjna)', editable=False, default=False)
    accept3 = models.BooleanField('Zgoda 3', editable=False, default=False)
    accept4 = models.BooleanField('Zgoda 4', editable=False, default=False)
    accept5 = models.BooleanField('Zgoda 5', editable=False, default=False)

    class Meta:
        db_table = 'marketing_lp_page_entry'
        verbose_name = u'wpis'
        verbose_name_plural = u'wpisy'

    def get_medium(self):
        medium = Medium.objects.filter(uid=self.medium).first()
        return medium or self.medium or '(Brak)'

    get_medium.short_description = 'Medium'

    def get_source(self):
        source = Source.objects.filter(uid=self.source).first()
        return source or self.source or '(Brak)'

    get_source.short_description = 'Źródło'
