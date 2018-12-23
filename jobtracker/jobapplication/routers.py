from rest_framework.routers import SimpleRouter

from .viewsets import CompanyViewset, JobReferenceViewset, JobApplicationViewset

job_application_router = SimpleRouter()
job_application_router.register('job_references', JobReferenceViewset)
job_application_router.register('companies', CompanyViewset)
job_application_router.register('job_applications', JobApplicationViewset)
