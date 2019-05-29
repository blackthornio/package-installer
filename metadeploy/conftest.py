import factory
import factory.fuzzy
import pytest
from allauth.socialaccount.models import SocialAccount, SocialApp, SocialToken
from django.contrib.auth import get_user_model
from pytest_factoryboy import register
from rest_framework.test import APIClient
from sfdo_template_helpers.crypto import fernet_encrypt

from metadeploy.api.models import (
    AllowedList,
    AllowedListOrg,
    Job,
    Plan,
    PlanSlug,
    PlanTemplate,
    PreflightResult,
    Product,
    ProductCategory,
    ProductSlug,
    Step,
    Version,
)

User = get_user_model()


@register
class SocialAppFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SocialApp
        django_get_or_create = ("provider",)

    name = "Salesforce Production"
    provider = "salesforce-production"
    key = "https://login.salesforce.com/"


@register
class SocialTokenFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SocialToken

    token = fernet_encrypt("0123456789abcdef")
    token_secret = fernet_encrypt("secret.0123456789abcdef")
    app = factory.SubFactory(SocialAppFactory)


@register
class SocialAccountFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SocialAccount

    provider = "salesforce-production"
    uid = factory.Sequence("https://example.com/{}".format)
    socialtoken_set = factory.RelatedFactory(SocialTokenFactory, "account")
    extra_data = {
        "instance_url": "https://example.com",
        "organization_details": {
            "Id": "00Dxxxxxxxxxxxxxxx",
            "Name": "Sample Org",
            "OrganizationType": "Developer Edition",
            "IsSandbox": False,
        },
    }


@register
class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Sequence("user_{}@example.com".format)
    username = factory.Sequence("user_{}@example.com".format)
    password = factory.PostGenerationMethodCall("set_password", "foobar")
    socialaccount_set = factory.RelatedFactory(SocialAccountFactory, "user")


@register
class AllowedListFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AllowedList

    title = factory.Sequence("Allowed List {}".format)


@register
class AllowedListOrgFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AllowedListOrg

    allowed_list = factory.SubFactory(AllowedListFactory)
    org_id = factory.fuzzy.FuzzyText(length=15, prefix="00D")
    description = factory.Sequence("Allowed List Org {}".format)
    created_by = factory.SubFactory(UserFactory)


@register
class ProductCategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProductCategory

    title = "salesforce"


@register
class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product

    title = factory.Sequence("Sample Product {}".format)
    description = "This is a sample product."
    category = factory.SubFactory(ProductCategoryFactory)
    color = "#FFFFFF"
    icon_url = ""
    slds_icon_category = ""
    slds_icon_name = ""
    _ensure_slug = factory.PostGenerationMethodCall("ensure_slug")
    repo_url = "https://github.com/SFDO-Tooling/CumulusCI-Test"


@register
class ProductSlugFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProductSlug

    slug = factory.Sequence("this-is-a-slug-{}".format)
    parent = factory.SubFactory(ProductFactory)


@register
class VersionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Version

    product = factory.SubFactory(ProductFactory)
    label = factory.Sequence("v0.{}.0".format)
    description = "A sample version."
    commit_ish = "feature/preflight"


@register
class PlanTemplateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PlanTemplate

    name = "install"
    preflight_message = ""
    post_install_message = ""
    product = factory.SubFactory(ProductFactory)


@register
class PlanFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Plan

    title = "Sample plan"
    _ensure_slug = factory.PostGenerationMethodCall("ensure_slug")
    preflight_flow_name = "slow_steps_preflight_good"

    visible_to = None

    version = factory.SubFactory(VersionFactory)
    plan_template = factory.SubFactory(
        PlanTemplateFactory, product=factory.SelfAttribute("..version.product")
    )


@register
class StepFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Step

    name = "Sample step"
    plan = factory.SubFactory(PlanFactory)
    path = "main_task"
    task_class = "cumulusci.core.tests.test_tasks._TaskHasResult"
    step_num = factory.Sequence("1.{}".format)


@register
class PlanSlugFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PlanSlug

    slug = factory.Sequence("this-is-a-slug-{}".format)
    parent = factory.SubFactory(PlanTemplateFactory)


@register
class JobFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Job

    user = factory.SubFactory(UserFactory)
    plan = factory.SubFactory(PlanFactory)
    enqueued_at = None
    job_id = None

    @factory.post_generation
    def steps(self, create, extracted, **kwargs):  # pragma: nocover
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of steps was passed in, use it
            for step in extracted:
                self.steps.add(step)


@register
class PreflightResultFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PreflightResult


@pytest.fixture
def client(user_factory):
    user = user_factory()
    client = APIClient()
    client.force_login(user)
    client.user = user
    return client


@pytest.fixture
def admin_api_client(user_factory):
    user = user_factory(is_superuser=True)
    client = APIClient()
    client.force_login(user)
    client.user = user
    return client


@pytest.fixture
def anon_client():
    return APIClient()
