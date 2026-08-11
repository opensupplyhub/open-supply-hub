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
from api.isic_taxonomy.errors import (
    IsicTaxonomyPublishError,
    IsicTaxonomyValidationError,
)
from api.isic_taxonomy.parser import normalize_extension
from api.isic_taxonomy.publisher import parse_and_validate, publish_taxonomy
from api.isic_taxonomy.runtime_config import invalidate_taxonomy_config_cache
from api.models.isic_taxonomy_config import IsicTaxonomyConfig


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


def isic_taxonomy_admin_view(request, admin_site):
    if not user_can_manage_isic_taxonomy(request.user):
        raise PermissionDenied

    config = IsicTaxonomyConfig.load()
    validation_errors = []
    preview_taxonomy = None
    preview_counts = None

    if request.method == 'POST':
        action = request.POST.get('action', '')

        if action in ('enable', 'disable'):
            _handle_toggle(request, config, enable=(action == 'enable'))
            return redirect('admin:isic_taxonomy')

        form = IsicTaxonomyUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded = form.cleaned_data.get('source_file')
            if not uploaded:
                messages.error(
                    request,
                    'Select a taxonomy spreadsheet before continuing.',
                )
            elif action == 'preview':
                validation_errors, preview_taxonomy, preview_counts = (
                    _handle_preview(uploaded)
                )
                if preview_taxonomy is not None:
                    messages.success(
                        request,
                        'Preview generated successfully. Review the hierarchy '
                        'below, then publish when ready.',
                    )
            elif action == 'publish':
                preview_taxonomy, preview_counts, validation_errors = (
                    _handle_publish(request, uploaded, config)
                )
            else:
                messages.error(request, 'Unknown action.')
        else:
            for field_errors in form.errors.values():
                for error in field_errors:
                    messages.error(request, error)
    else:
        form = IsicTaxonomyUploadForm()

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
