from django import template
from ..models import JobForTest,MyTagForEptest,TaggedWhateverForEptest
from django.db.models import Count, Q


register = template.Library()

@register.simple_tag(name='total_jobs')
def total_jobs():
    return JobForTest.published.count()

@register.inclusion_tag('latest_jobs.html')
def show_latest_jobs(count=5):
    latest_jobs = JobForTest.published.order_by('-publish')[:count]
    return {'latest_jobs': latest_jobs}

@register.simple_tag
def get_tags():
    return MyTagForEptest.objects.all()


@register.simple_tag
def get_tags_count():
    # result = TaggedWhatever.objects.values('tag_id').order_by('tag_id').annotate(count=Count('tag_id')).order_by('count')
    result = TaggedWhateverForEptest.objects.values('tag_id').annotate(count=Count('tag_id')).order_by('-count')
    print(result,type(result))

    tag_list=[]
    for each in result:
        # print(each["tag_id"],each["count"])
        tag_one=MyTagForEptest.objects.get(id=each["tag_id"])
        tag_list.append((tag_one.id,tag_one.name,tag_one.slug,each["count"]))

    return tag_list

