from ..constants import MASKED_CONTRIBUTOR_LABEL
from ..helpers.helpers import prefix_a_an
from ..models import Contributor, EmbedConfig


def is_embed_mode_active(serializer):
    if serializer.context is None:
        return False
    request = serializer.context.get("request")
    return (
        request is not None
        and request.query_params is not None
        and request.query_params.get("embed") == "1"
    )


def get_embed_contributor_id_from_query_params(query_params):
    contributor = query_params.get("contributor", None)
    if contributor is None:
        contributors = query_params.getlist("contributors", [])
        if not contributors:
            return None
        contributor = contributors[0]
    return contributor


def get_embed_contributor_id(serializer):
    request = (
        serializer.context.get("request")
        if serializer.context is not None
        else None
    )

    if request is None or request.query_params is None:
        return None
    contributor = get_embed_contributor_id_from_query_params(
        request.query_params
    )
    return contributor


def prefer_contributor_name(serializer):
    try:
        contributor_id = get_embed_contributor_id(serializer)
        if is_embed_mode_active(serializer) and contributor_id is not None:
            contributor = Contributor.objects.get(id=contributor_id)
            if contributor.embed_level is not None:
                config = EmbedConfig.objects.get(contributor=contributor)
                return config.prefer_contributor_name
        return False
    except EmbedConfig.DoesNotExist:
        return False
    except Contributor.DoesNotExist:
        return False


def is_contribution_masked(contributor, masked):
    return bool(masked) and masked.should_mask(contributor)


def is_attributed_to_organization(contributor):
    """
    Whether a contributor blob of the FacilityIndex JSON stands for an
    organization. The index functions then carry the organization's name
    in place of the member's contributor name and mark the blob with
    organization_id. The ids in it are still the member's, so they are
    not published: the organization has no public profile to link to.
    """
    return bool(contributor) and contributor.get('organization_id') is not None


def get_contributor_name(contributor, user_can_see_detail, masked=None):
    if (
        (contributor is None)
        or (contributor["name"] is None)
        or (contributor["contrib_type"] is None)
    ):
        return None
    if is_contribution_masked(contributor, masked):
        return MASKED_CONTRIBUTOR_LABEL
    if user_can_see_detail:
        return contributor["name"]
    name = prefix_a_an(contributor["contrib_type"])
    return name[0].lower() + name[1:]


def get_contributor_id(contributor, user_can_see_detail, masked=None):
    if is_contribution_masked(contributor, masked):
        return None
    if is_attributed_to_organization(contributor):
        return None
    if (
        contributor is not None
        and contributor["admin_id"] is not None
        and user_can_see_detail
    ):
        return contributor["admin_id"]
    return None
