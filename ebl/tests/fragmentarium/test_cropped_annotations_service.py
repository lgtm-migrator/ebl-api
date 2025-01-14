from ebl.fragmentarium.application.cropped_annotations_service import (
    CroppedAnnotationService,
)
from ebl.fragmentarium.application.cropped_sign_image import (
    Base64,
    CroppedSignImage,
    CroppedAnnotation,
)
from ebl.tests.factories.annotation import (
    AnnotationsFactory,
    AnnotationFactory,
)


def test_find_annotations_by_sign(
    annotations_repository, cropped_sign_images_repository, when
):
    service = CroppedAnnotationService(
        annotations_repository, cropped_sign_images_repository
    )
    annotation = AnnotationFactory.build_batch(2)
    annotations = AnnotationsFactory.build(annotations=annotation)

    image_id_1 = annotation[0].cropped_sign.image_id
    image_id_2 = annotation[1].cropped_sign.image_id

    when(annotations_repository).find_by_sign("test-sign").thenReturn([annotations])
    when(cropped_sign_images_repository).query_by_id(image_id_1).thenReturn(
        CroppedSignImage(image_id_1, Base64("test-base64-1"))
    )
    when(cropped_sign_images_repository).query_by_id(image_id_2).thenReturn(
        CroppedSignImage(image_id_2, Base64("test-base64-2"))
    )
    fragment_number = annotations.fragment_number
    expected_1 = CroppedAnnotation.from_cropped_sign(
        fragment_number, Base64("test-base64-1"), annotation[0].cropped_sign
    )
    expected_2 = CroppedAnnotation.from_cropped_sign(
        fragment_number, Base64("test-base64-2"), annotation[1].cropped_sign
    )
    assert service.find_annotations_by_sign("test-sign") == [expected_1, expected_2]
