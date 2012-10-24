from django.conf.urls import patterns, include, url
from django.views.generic.base import TemplateView
from calebasse.cbv import ListView, CreateView, DeleteView, UpdateView

from models import Office

#         AnnexeEtablissement, CaisseAssuranceMaladie,
#        CompagnieDeTransport, CodeCFTMEA, CodeDeNonFacturation, Etablissement,
#        LieuDeScolarisation, MotifInscription, Nationalite, Profession, Salle,
#        TarifDesSeance, TypeActes, TypeAutoriteParentale, TypeDeConseilleur,
#        TypeDeGardesParentales, TypeDeSeances, TypeDeSituationFamiliale,
#        TypeDeTransport)

office_patterns = patterns('',
    url(r'^$',
        ListView.as_view(model=Office),
        name='annexe-etablissement'),
    url(r'^new/$',
        CreateView.as_view(model=Office,
        template_name_suffix='_default_new.html'),
        name='annexe-etablissement-nouveau'),
    url(r'^(?P<pk>\d+)/$',
        UpdateView.as_view(model=Office,
        template_name_suffix='_edit.html'),
        name='annexe-etablissement-edit'),
    url(r'^(?P<pk>\d+)/delete/$',
        DeleteView.as_view(model=Office),
        name='annexe-etablissement-supprimer'),
)

urlpatterns = patterns('',
    url(r'^$',
        TemplateView.as_view(template_name='ressources/index.html')),
    url(r'^annexe-etablissement/',
        include(office_patterns))
    )


#caisse_assurances_maladie_patterns = patterns('',
#    url(r'^$',
#        ListView.as_view(model=CaisseAssuranceMaladie),
#        name='caisse-assurances-maladie'),
#    url(r'^nouveau/$',
#        CreateView.as_view(model=CaisseAssuranceMaladie,
#        template_name_suffix='_default_nouveau.html'),
#        name='caisse-assurances-maladie-nouveau'),
#    url(r'^(?P<pk>\d+)/$',
#        UpdateView.as_view(model=CaisseAssuranceMaladie,
#        template_name_suffix='_edit.html'),
#        name='caisse-assurances-maladie-edit'),
#    url(r'^(?P<pk>\d+)/supprimer/$',
#        DeleteView.as_view(model=CaisseAssuranceMaladie),
#        name='caisse-assurances-maladie-supprimer'),
#)
#
#
#compagnie_transport_patterns = patterns('',
#    url(r'^$',
#        ListView.as_view(model=CompagnieDeTransport),
#        name='compagnie-transport'),
#    url(r'^nouveau/$',
#        CreateView.as_view(model=CompagnieDeTransport,
#        template_name_suffix='_default_nouveau.html'),
#        name='compagnie-transport-nouveau'),
#    url(r'^(?P<pk>\d+)/$',
#        UpdateView.as_view(model=CompagnieDeTransport,
#        template_name_suffix='_edit.html'),
#        name='compagnie-transport-edit'),
#    url(r'^(?P<pk>\d+)/supprimer/$',
#        DeleteView.as_view(model=CompagnieDeTransport),
#        name='compagnie-transport-supprimer'),
#)
#
#
#code_cftmea_patterns = patterns('',
#    url(r'^$',
#        ListView.as_view(model=CodeCFTMEA),
#        name='code-cftmea'),
#    url(r'^nouveau/$',
#        CreateView.as_view(model=CodeCFTMEA,
#        template_name_suffix='_default_nouveau.html'),
#        name='code-cftmea-nouveau'),
#    url(r'^(?P<pk>\d+)/$',
#        UpdateView.as_view(model=CodeCFTMEA,
#        template_name_suffix='_edit.html'),
#        name='code-cftmea-edit'),
#    url(r'^(?P<pk>\d+)/supprimer/$',
#        DeleteView.as_view(model=CodeCFTMEA),
#        name='code-cftmea-supprimer'),
#)
#
#
#code_non_facturation_patterns = patterns('',
#    url(r'^$',
#        ListView.as_view(model=CodeDeNonFacturation),
#        name='code-non-facturation'),
#    url(r'^nouveau/$',
#        CreateView.as_view(model=CodeDeNonFacturation,
#        template_name_suffix='_default_nouveau.html'),
#        name='code-non-facturation-nouveau'),
#    url(r'^(?P<pk>\d+)/$',
#        UpdateView.as_view(model=CodeDeNonFacturation,
#        template_name_suffix='_edit.html'),
#        name='code-non-facturation-edit'),
#    url(r'^(?P<pk>\d+)/supprimer/$',
#        DeleteView.as_view(model=CodeDeNonFacturation),
#        name='code-non-facturation-supprimer'),
#)
#
#
#etablissement_patterns = patterns('',
#    url(r'^$',
#        ListView.as_view(model=Etablissement),
#        name='etablissement'),
#    url(r'^nouveau/$',
#        CreateView.as_view(model=Etablissement,
#        template_name_suffix='_default_nouveau.html'),
#        name='etablissement-nouveau'),
#    url(r'^(?P<pk>\d+)/$',
#        UpdateView.as_view(model=Etablissement,
#        template_name_suffix='_edit.html'),
#        name='etablissement-edit'),
#    url(r'^(?P<pk>\d+)/supprimer/$',
#        DeleteView.as_view(model=Etablissement),
#        name='etablissement-supprimer'),
#)
#
#
#lieu_scolarisation_patterns = patterns('',
#    url(r'^$',
#        ListView.as_view(model=LieuDeScolarisation),
#        name='lieu-scolarisation'),
#    url(r'^nouveau/$',
#        CreateView.as_view(model=LieuDeScolarisation,
#        template_name_suffix='_default_nouveau.html'),
#        name='lieu-scolarisation-nouveau'),
#    url(r'^(?P<pk>\d+)/$',
#        UpdateView.as_view(model=LieuDeScolarisation,
#        template_name_suffix='_edit.html'),
#        name='lieu-scolarisation-edit'),
#    url(r'^(?P<pk>\d+)/supprimer/$',
#        DeleteView.as_view(model=LieuDeScolarisation),
#        name='lieu-scolarisation-supprimer'),
#)
#
#
#motif_inscription_patterns = patterns('',
#    url(r'^$',
#        ListView.as_view(model=MotifInscription),
#        name='motif-inscription'),
#    url(r'^nouveau/$',
#        CreateView.as_view(model=MotifInscription,
#        template_name_suffix='_default_nouveau.html'),
#        name='motif-inscription-nouveau'),
#    url(r'^(?P<pk>\d+)/$',
#        UpdateView.as_view(model=MotifInscription,
#        template_name_suffix='_edit.html'),
#        name='motif-inscription-edit'),
#    url(r'^(?P<pk>\d+)/supprimer/$',
#        DeleteView.as_view(model=MotifInscription),
#        name='motif-inscription-supprimer'),
#)
#
#
#nationalite_patterns = patterns('',
#    url(r'^$',
#        ListView.as_view(model=Nationalite),
#        name='nationalite'),
#    url(r'^nouveau/$',
#        CreateView.as_view(model=Nationalite,
#        template_name_suffix='_default_nouveau.html'),
#        name='nationalite-nouveau'),
#    url(r'^(?P<pk>\d+)/$',
#        UpdateView.as_view(model=Nationalite,
#        template_name_suffix='_edit.html'),
#        name='nationalite-edit'),
#    url(r'^(?P<pk>\d+)/supprimer/$',
#        DeleteView.as_view(model=Nationalite),
#        name='nationalite-supprimer'),
#)
#
#
#profession_patterns = patterns('',
#    url(r'^$',
#        ListView.as_view(model=Profession),
#        name='profession'),
#    url(r'^nouveau/$',
#        CreateView.as_view(model=Profession,
#        template_name_suffix='_default_nouveau.html'),
#        name='profession-nouveau'),
#    url(r'^(?P<pk>\d+)/$',
#        UpdateView.as_view(model=Profession,
#        template_name_suffix='_edit.html'),
#        name='profession-edit'),
#    url(r'^(?P<pk>\d+)/supprimer/$',
#        DeleteView.as_view(model=Profession),
#        name='profession-supprimer'),
#)
#
#
#salles_patterns = patterns('',
#    url(r'^$',
#        ListView.as_view(model=Salle),
#        name='salles'),
#    url(r'^nouveau/$',
#        CreateView.as_view(model=Salle,
#        template_name_suffix='_default_nouveau.html'),
#        name='salles-nouveau'),
#    url(r'^(?P<pk>\d+)/$',
#        UpdateView.as_view(model=Salle,
#        template_name_suffix='_edit.html'),
#        name='salles-edit'),
#    url(r'^(?P<pk>\d+)/supprimer/$',
#        DeleteView.as_view(model=Salle),
#        name='salles-supprimer'),
#)
#
#
#tarif_des_seances_patterns = patterns('',
#    url(r'^$',
#        ListView.as_view(model=TarifDesSeance),
#        name='tarif-des-seances'),
#    url(r'^nouveau/$',
#        CreateView.as_view(model=TarifDesSeance,
#        template_name_suffix='_default_nouveau.html'),
#        name='tarif-des-seances-nouveau'),
#    url(r'^(?P<pk>\d+)/$',
#        UpdateView.as_view(model=TarifDesSeance,
#        template_name_suffix='_edit.html'),
#        name='tarif-des-seances-edit'),
#    url(r'^(?P<pk>\d+)/supprimer/$',
#        DeleteView.as_view(model=TarifDesSeance),
#        name='tarif-des-seances-supprimer'),
#)
#
#
#type_actes_patterns = patterns('',
#    url(r'^$',
#        ListView.as_view(model=TypeActes),
#        name='type-actes'),
#    url(r'^nouveau/$',
#        CreateView.as_view(model=TypeActes,
#        template_name_suffix='_default_nouveau.html'),
#        name='type-actes-nouveau'),
#    url(r'^(?P<pk>\d+)/$',
#        UpdateView.as_view(model=TypeActes,
#        template_name_suffix='_edit.html'),
#        name='type-actes-edit'),
#    url(r'^(?P<pk>\d+)/supprimer/$',
#        DeleteView.as_view(model=TypeActes),
#        name='type-actes-supprimer'),
#)
#
#
#type_autorite_parentale_patterns = patterns('',
#    url(r'^$',
#        ListView.as_view(model=TypeAutoriteParentale),
#        name='type-autorite-parentale'),
#    url(r'^nouveau/$',
#        CreateView.as_view(model=TypeAutoriteParentale,
#        template_name_suffix='_default_nouveau.html'),
#        name='type-autorite-parentale-nouveau'),
#    url(r'^(?P<pk>\d+)/$',
#        UpdateView.as_view(model=TypeAutoriteParentale,
#        template_name_suffix='_edit.html'),
#        name='type-autorite-parentale-edit'),
#    url(r'^(?P<pk>\d+)/supprimer/$',
#        DeleteView.as_view(model=TypeAutoriteParentale),
#        name='type-autorite-parentale-supprimer'),
#)
#
#
#types_conseilleurs_patterns = patterns('',
#    url(r'^$',
#        ListView.as_view(model=TypeDeConseilleur),
#        name='types-conseilleurs'),
#    url(r'^nouveau/$',
#        CreateView.as_view(model=TypeDeConseilleur,
#        template_name_suffix='_default_nouveau.html'),
#        name='types-conseilleurs-nouveau'),
#    url(r'^(?P<pk>\d+)/$',
#        UpdateView.as_view(model=TypeDeConseilleur,
#        template_name_suffix='_edit.html'),
#        name='types-conseilleurs-edit'),
#    url(r'^(?P<pk>\d+)/supprimer/$',
#        DeleteView.as_view(model=TypeDeConseilleur),
#        name='types-conseilleurs-supprimer'),
#)
#
#
#type_gardes_parentales_patterns = patterns('',
#    url(r'^$',
#        ListView.as_view(model=TypeDeGardesParentales),
#        name='type-gardes-parentales'),
#    url(r'^nouveau/$',
#        CreateView.as_view(model=TypeDeGardesParentales,
#        template_name_suffix='_default_nouveau.html'),
#        name='type-gardes-parentales-nouveau'),
#    url(r'^(?P<pk>\d+)/$',
#        UpdateView.as_view(model=TypeDeGardesParentales,
#        template_name_suffix='_edit.html'),
#        name='type-gardes-parentales-edit'),
#    url(r'^(?P<pk>\d+)/supprimer/$',
#        DeleteView.as_view(model=TypeDeGardesParentales),
#        name='type-gardes-parentales-supprimer'),
#)
#
#
#type_seance_patterns = patterns('',
#    url(r'^$',
#        ListView.as_view(model=TypeDeSeances),
#        name='type-seance'),
#    url(r'^nouveau/$',
#        CreateView.as_view(model=TypeDeSeances,
#        template_name_suffix='_default_nouveau.html'),
#        name='type-seance-nouveau'),
#    url(r'^(?P<pk>\d+)/$',
#        UpdateView.as_view(model=TypeDeSeances,
#        template_name_suffix='_edit.html'),
#        name='type-seance-edit'),
#    url(r'^(?P<pk>\d+)/supprimer/$',
#        DeleteView.as_view(model=TypeDeSeances),
#        name='type-seance-supprimer'),
#)
#
#
#type_situation_familiale_patterns = patterns('',
#    url(r'^$',
#        ListView.as_view(model=TypeDeSituationFamiliale),
#        name='type-situation-familiale'),
#    url(r'^nouveau/$',
#        CreateView.as_view(model=TypeDeSituationFamiliale,
#        template_name_suffix='_default_nouveau.html'),
#        name='type-situation-familiale-nouveau'),
#    url(r'^(?P<pk>\d+)/$',
#        UpdateView.as_view(model=TypeDeSituationFamiliale,
#        template_name_suffix='_edit.html'),
#        name='type-situation-familiale-edit'),
#    url(r'^(?P<pk>\d+)/supprimer/$',
#        DeleteView.as_view(model=TypeDeSituationFamiliale),
#        name='type-situation-familiale-supprimer'),
#)
#
#
#type_transport_patterns = patterns('',
#    url(r'^$',
#        ListView.as_view(model=TypeDeTransport),
#        name='type-transport'),
#    url(r'^nouveau/$',
#        CreateView.as_view(model=TypeDeTransport,
#        template_name_suffix='_default_nouveau.html'),
#        name='type-transport-nouveau'),
#    url(r'^(?P<pk>\d+)/$',
#        UpdateView.as_view(model=TypeDeTransport,
#        template_name_suffix='_edit.html'),
#        name='type-transport-edit'),
#    url(r'^(?P<pk>\d+)/supprimer/$',
#        DeleteView.as_view(model=TypeDeTransport),
#        name='type-transport-supprimer'),
#)
#
#
#urlpatterns = patterns('',
#    url(r'^$',
#        TemplateView.as_view(template_name='ressources/index.html')),
#    url(r'^annexe-etablissement/',
#        include(annexe_etablissement_patterns)),
#    url(r'^caisse-assurances-maladie/',
#        include(caisse_assurances_maladie_patterns)),
#    url(r'^compagnie-transport/',
#        include(compagnie_transport_patterns)),
#    url(r'^code-cftmea/',
#        include(code_cftmea_patterns)),
#    url(r'^code-non-facturation/',
#        include(code_non_facturation_patterns)),
#    url(r'^etablissement/',
#        include(etablissement_patterns)),
#    url(r'^lieu-scolarisation/',
#        include(lieu_scolarisation_patterns)),
#    url(r'^motif-inscription/',
#        include(motif_inscription_patterns)),
#    url(r'^nationalite/',
#        include(nationalite_patterns)),
#    url(r'^profession/',
#        include(profession_patterns)),
#    url(r'^salles/',
#        include(salles_patterns)),
#    url(r'^tarif-des-seances/',
#        include(tarif_des_seances_patterns)),
#    url(r'^type-actes/',
#        include(type_actes_patterns)),
#    url(r'^type-autorite-parentale/',
#        include(type_autorite_parentale_patterns)),
#    url(r'^types-conseilleurs/',
#        include(types_conseilleurs_patterns)),
#    url(r'^type-gardes-parentales/',
#        include(type_gardes_parentales_patterns)),
#    url(r'^type-seance/',
#        include(type_seance_patterns)),
#    url(r'^type-situation-familiale/',
#        include(type_situation_familiale_patterns)),
#    url(r'^type-transport/',
#        include(type_transport_patterns)),
#)

