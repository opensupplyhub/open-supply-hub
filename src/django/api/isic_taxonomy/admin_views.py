import logging

from django import forms
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.core.files.base import ContentFile
from django.shortcuts import redirect, render

from api.isic_taxonomy.builder import count_taxonomy_levels
from api.isic_taxonomy.constants import (
    ALLOWED_EXTENSIONS,
    LABEL_CHAR_PATTERN,
    MAX_FILE_SIZE_BYTES,
    REQUIRED_HEADERS,
)
from api.isic_taxonomy.content import (
    IsicTaxonomyNotAvailable,
    load_published_isic4_taxonomy,
)
from api.isic_taxonomy.errors import (
    IsicTaxonomyPublishError,
    IsicTaxonomyValidationError,
)
from api.isic_taxonomy.parser import normalize_extension
from api.isic_taxonomy.publisher import parse_and_validate, publish_taxonomy
from api.isic_taxonomy.runtime_config import invalidate_taxonomy_config_cache
from api.models.isic_taxonomy_config import IsicTaxonomyConfig

logger = logging.getLogger(__name__)


class IsicTaxonomyUploadForm(forms.Form):
    source_file = forms.FileField(
        label='Taxonomy spreadsheet',
        required=False,
        help_text='CSV, XLSX, or ODS file (max 5 MB).',
    )

    def clean_source_file(self):
        uploaded = self.cleaned_data.get('source_file')
        if not uploaded:
            return uploaded

        if uploaded.size > MAX_FILE_SIZE_BYTES:
            max_mb = MAX_FILE_SIZE_BYTES // (1024 * 1024)
            raise forms.ValidationError(
                f'File exceeds the {max_mb} MB size limit.'
            )

        extension = normalize_extension(uploaded.name)
        if extension not in ALLOWED_EXTENSIONS:
            allowed = ', '.join(sorted(ALLOWED_EXTENSIONS))
            raise forms.ValidationError(
                f'Unsupported file type "{extension}". '
                f'Accepted formats: {allowed}.'
            )

        return uploaded


def user_can_manage_isic_taxonomy(user) -> bool:
    return (
        user.is_active
        and user.is_staff
        and user.has_perm('api.change_isictaxonomyconfig')
    )


def get_isic_taxonomy_admin_url():
    from django.urls import reverse

    return reverse('admin:api_isictaxonomyconfig_changelist')


def isic_taxonomy_admin_view(request, admin_site):
    if not user_can_manage_isic_taxonomy(request.user):
        raise PermissionDenied

    admin_url = get_isic_taxonomy_admin_url()
    config = IsicTaxonomyConfig.load()
    form = IsicTaxonomyUploadForm()
    validation_errors = []
    preview_taxonomy = None
    preview_counts = None

    if request.method == 'POST':
        (
            redirect_response,
            form,
            validation_errors,
            preview_taxonomy,
            preview_counts,
        ) = _handle_post_request(request, config, admin_url)
        if redirect_response is not None:
            return redirect_response

    if preview_taxonomy is None:
        preview_taxonomy, preview_counts = _load_published_taxonomy_preview(
            config,
        )

    context = {
        **admin_site.each_context(request),
        'title': 'ISIC Taxonomy',
        'subtitle': None,
        'config': config,
        'form': form,
        'validation_errors': validation_errors,
        'preview_taxonomy': preview_taxonomy,
        'preview_counts': preview_counts,
        'required_headers': REQUIRED_HEADERS,
        'allowed_extensions': sorted(ALLOWED_EXTENSIONS),
        'max_file_size_mb': MAX_FILE_SIZE_BYTES // (1024 * 1024),
        'label_char_pattern': LABEL_CHAR_PATTERN.pattern,
        'opts': IsicTaxonomyConfig._meta,
        'has_permission': True,
    }
    return render(request, 'admin/isic_taxonomy.html', context)


def _handle_post_request(request, config, admin_url):
    action = request.POST.get('action', '')

    if action in ('enable', 'disable'):
        _handle_toggle(request, config, enable=(action == 'enable'))
        return redirect(admin_url), None, [], None, None

    form = IsicTaxonomyUploadForm(request.POST, request.FILES)
    if not form.is_valid():
        for field_errors in form.errors.values():
            for error in field_errors:
                messages.error(request, error)
        return None, form, [], None, None

    uploaded = form.cleaned_data.get('source_file')
    if not uploaded:
        messages.error(
            request,
            'Select a taxonomy spreadsheet before continuing.',
        )
        return None, form, [], None, None

    if action == 'preview':
        validation_errors, preview_taxonomy, preview_counts = (
            _handle_preview(uploaded)
        )
        if preview_taxonomy is not None:
            messages.success(
                request,
                'Preview generated successfully. Review the hierarchy '
                'below, then publish when ready.',
            )
        return None, form, validation_errors, preview_taxonomy, preview_counts

    if action == 'publish':
        preview_taxonomy, preview_counts, validation_errors = (
            _handle_publish(request, uploaded, config)
        )
        return None, form, validation_errors, preview_taxonomy, preview_counts

    messages.error(request, 'Unknown action.')
    return None, form, [], None, None


def _load_published_taxonomy_preview(config):
    if not config.json_s3_key:
        return None, None

    try:
        taxonomy = load_published_isic4_taxonomy(config=config)
    except IsicTaxonomyNotAvailable:
        return None, None
    except Exception:
        logger.exception('Failed to load published ISIC taxonomy for admin')
        return None, None

    return taxonomy, count_taxonomy_levels(taxonomy)


def _handle_toggle(request, config, *, enable: bool) -> None:
    config.is_active = enable
    config.save(update_fields=['is_active', 'updated_at'])
    invalidate_taxonomy_config_cache()
    if enable:
        messages.success(
            request,
            'ISIC Rev 4 taxonomy is now enabled in extended search.',
        )
    else:
        messages.success(
            request,
            'ISIC Rev 4 taxonomy is now disabled in extended search.',
        )


def _handle_preview(uploaded):
    file_content = uploaded.read()
    try:
        taxonomy = parse_and_validate(file_content, uploaded.name)
    except IsicTaxonomyValidationError as exc:
        return [error.format() for error in exc.errors], None, None

    counts = count_taxonomy_levels(taxonomy)
    return [], taxonomy, counts


def _handle_publish(request, uploaded, config):
    file_content = uploaded.read()
    try:
        result = publish_taxonomy(
            file_content=file_content,
            filename=uploaded.name,
            uploaded_by=request.user,
            activate=True,
        )
    except IsicTaxonomyValidationError as exc:
        return None, None, [error.format() for error in exc.errors]
    except IsicTaxonomyPublishError as exc:
        messages.error(
            request,
            f'Publish failed: {exc}. The previous active version was kept.',
        )
        config.refresh_from_db()
        return None, None, []

    config.refresh_from_db()
    config.source_filename = uploaded.name
    config.source_file.save(
        uploaded.name,
        ContentFile(file_content),
        save=True,
    )

    counts = result['counts']
    messages.success(
        request,
        (
            f'Published ISIC taxonomy version {result["version"]} '
            f'({counts["class_count"]} classes).'
        ),
    )
    return result['taxonomy'], counts, []
