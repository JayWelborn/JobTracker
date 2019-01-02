from rest_framework.routers import SimpleRouter

from .viewsets import CompanyViewset, JobReferenceViewset, JobApplicationViewset

job_application_router = SimpleRouter()
job_application_router.register('job_references', JobReferenceViewset,
                                base_name='jobreference')
job_application_router.register('companies', CompanyViewset,
                                base_name='company')
job_application_router.register('jobapplications', JobApplicationViewset,
                                base_name='jobapplication')
