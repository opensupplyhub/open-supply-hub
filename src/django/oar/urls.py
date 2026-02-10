"""oar URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.urls import path, include

from api import views
from api.views.v1.production_locations \
     import ProductionLocations
from api.views.v1.moderation_events \
     import ModerationEvents
from api.views.stripe.download_locations_checkout_session_view \
     import DownloadLocationsCheckoutSessionView
from api.views.stripe.download_locations_checkout_webhook_view \
     import DownloadLocationsCheckoutWebhookView
from api.admin import admin_site
from api.facilities_download_view_set import FacilitiesDownloadViewSet
from web.views import environment

from rest_framework import routers, permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from oar import settings
from api.views.v1.url_names import URLNames


router = routers.DefaultRouter()
router.register('facility-lists', views.FacilityListViewSet, 'facility-list')
router.register('facilities', views.FacilitiesViewSet, 'facility')
router.register('facility-claims', views.FacilityClaimViewSet,
                'facility-claim')
router.register('facility-matches', views.FacilityMatchViewSet,
                'facility-match')
router.register('api-blocks', views.ApiBlockViewSet, 'api-block')
router.register('facility-activity-reports',
                views.FacilityActivityReportViewSet,
                'facility-activity-report')
router.register('embed-configs', views.EmbedConfigViewSet, 'embed-config')
router.register('nonstandard-fields', views.NonstandardFieldsViewSet,
                'nonstandard-fields')
router.register('facilities-downloads', FacilitiesDownloadViewSet,
                'facilities-downloads')
router.register('moderation-events', views.ModerationEventsViewSet,
                'moderation-event')

v1_router = routers.DefaultRouter()
v1_router.register(
    URLNames.PRODUCTION_LOCATIONS,
    ProductionLocations,
    basename=URLNames.PRODUCTION_LOCATIONS
)
v1_router.register(
    URLNames.MODERATION_EVENTS,
    ModerationEvents,
    basename=URLNames.MODERATION_EVENTS
)

v1_custom_routes = [
     path(
          'download-locations-checkout-session/',
          DownloadLocationsCheckoutSessionView.as_view(),
          name='download-locations-checkout-session'
     ),
     path(
          'download-locations-checkout-webhook/',
          DownloadLocationsCheckoutWebhookView.as_view(),
          name='download-locations-checkout-webhook'
     ),
]

public_apis = [
    path('api/', include(router.urls)),
    path('api/contributors/active_count/', views.active_contributors_count,
         name='active_contributors_count'),
    path('api/contributors/', views.all_contributors,
         name='all_contributors'),
    path('api/contributor-embed-configs/<int:pk>/',
         views.contributor_embed_config, name='contributor-embed-config'),
    path('api/contributor-types/', views.all_contributor_types,
         name='all_contributor_types'),
    path('api/countries/active_count/', views.active_countries_count,
         name='active_countries_count'),
    path('api/countries/', views.all_countries, name='all_countries'),
    path('api/contributor-lists/',
         views.ContributorFacilityListViewSet.as_view({'get': 'list'}),
         name='contributor_lists'),
    path('api/contributor-lists-sorted/',
         views.ContributorFacilityListSortedViewSet.as_view({'get': 'list'}),
         name='contributor_lists_sorted'),
    path('api/log-download/', views.log_download, name='log_download'),
    path('api/workers-ranges/', views.number_of_workers_ranges,
         name='number_of_workers_ranges'),
    path('api/claim-statuses/', views.claim_statuses, name='claim_statuses'),
    path('api/facility-processing-types/', views.facility_processing_types,
         name='facility_processing_types'),
    path('api/parent-companies/', views.parent_companies,
         name='parent_companies'),
    path('api/product-types/', views.product_types, name='product_types'),
    path('api/sectors/', views.sectors, name='sectors'),
    path(
        'api/partner-fields/',
        views.PartnerFieldsViewSet.as_view({'get': 'list'}),
        name='partner_fields'
    ),
]

api_v1 = [path('api/v1/', include(v1_router.urls + v1_custom_routes))]

schema_view = get_schema_view(
    openapi.Info(
        title='Open Supply Hub API',
        default_version='1',
        description='Open Supply Hub API',
        terms_of_service="https://info.opensupplyhub.org/terms-of-service",
        license=openapi.License(name='MIT', url='https://github.com/opensupplyhub/open-supply-hub/blob/main/LICENSE.txt')  # NOQA
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    patterns=[path("", include(public_apis + api_v1))],
)

info_apis = [
    path('api/info/contributors/', views.active_contributors_count,
         name='active_contributors_count'),
    path('api/info/countries/', views.active_countries_count,
         name='active_countries_count'),
    path('api/info/facilities/',
         views.FacilitiesViewSet.as_view({'get': 'count'}),
         name='facilities_count'),
]

internal_apis = [
    path('', include('django.contrib.auth.urls')),
    path('web/environment.js', environment, name='environment'),
    path('api/docs/', schema_view.with_ui('swagger'),
         name='schema-swagger-ui'),
    path('admin/', admin_site.urls),
    path('accounts/', include('allauth.urls')),
    path('ckeditor5/', include('django_ckeditor_5.urls')),
    path('health-check/', include('watchman.urls')),
    path('api-auth/', include('rest_framework.urls')),
    path('rest-auth/', include('dj_rest_auth.urls')),
    path('rest-auth/registration/', include('dj_rest_auth.registration.urls')),
    path('user-login/', views.LoginToOARClient.as_view(),
         name='login_to_oar_client'),
    path('user-logout/', views.LogoutOfOARClient.as_view(),
         name='logout_of_oar_client'),
    path('user-signup/', views.SubmitNewUserForm.as_view(),
         name='submit_new_user_form'),
    path('user-profile/<int:pk>/', views.UserProfile.as_view(),
         name='get_and_update_user_profile'),
    path('api-token-auth/', views.APIAuthToken.as_view(),
         name='api_token_auth'),
    path('user-api-info/<int:uid>/',
         views.UserAPIInfo.as_view(),
         name='user-api-info'),
    path('api-feature-flags/', views.api_feature_flags,
         name='api_feature_flags'),
    path('tile/<layer>/<cachekey>/<int:z>/<int:x>/<int:y>.<ext>',
         views.get_tile, name='tile'),
    path('api/current_tile_cache_key/', views.current_tile_cache_key),
    path(
        'api-blocks/',
        views.ApiBlockViewSet.as_view({'get': 'list'}),
        name='api-block-internal',
    ),
    path('api/admin-facility-lists/', views.AdminFacilityListView.as_view(),
         name='admin-facility-lists'),
    path('api/geocoder/', views.get_geocoding, name='get_geocoding'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


urlpatterns = public_apis + api_v1 + internal_apis + info_apis
