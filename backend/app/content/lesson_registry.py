from typing import Dict, List, Optional
from app.content.schemas import LessonContent

class LessonRegistry:
    """
    Production Scalable Lesson Content Registry:
    Provides rich structured lesson content for ASL Alphabet signs A-E,
    with automatic fallback generation for A-Z.
    """
    def __init__(self):
        self._lessons: Dict[str, LessonContent] = {}
        self._initialize_sample_lessons()

    def _initialize_sample_lessons(self):
        # Lesson A
        self._lessons['A'] = LessonContent(
            sign='A',
            description="Form a firm fist with the thumb resting vertically along the side of the index finger.",
            meaning="Letter 'A' in the ASL manual alphabet.",
            reference_image="/assets/signs/A.png",
            optional_video="/assets/videos/A.mp4",
            difficulty="Easy",
            instructions=[
                "Make a tight fist with your dominant hand.",
                "Keep all four fingers folded firmly into your palm.",
                "Place your thumb upright alongside your index finger (do not fold thumb across fingers)."
            ],
            common_mistakes=[
                "Tucking the thumb inside the folded fingers (looks like 'S' or 'E').",
                "Leaving fingers loosely open."
            ],
            example_usage="Used for spelling words like 'APPLE' or 'ALWAYS'.",
            course_module_relation="ASL Alphabet Foundations - Module 1"
        )

        # Lesson B
        self._lessons['B'] = LessonContent(
            sign='B',
            description="Extend four fingers straight upward together while folding the thumb across the palm.",
            meaning="Letter 'B' in the ASL manual alphabet.",
            reference_image="/assets/signs/B.png",
            optional_video="/assets/videos/B.mp4",
            difficulty="Easy",
            instructions=[
                "Hold your hand flat with palm facing forward.",
                "Extend index, middle, ring, and pinky fingers straight upward pressed together.",
                "Cross your thumb horizontally across your palm."
            ],
            common_mistakes=[
                "Spreading fingers apart (looks like open palm or number 4).",
                "Leaving thumb sticking out to the side."
            ],
            example_usage="Used for spelling words like 'BOOK' or 'BEAUTIFUL'.",
            course_module_relation="ASL Alphabet Foundations - Module 1"
        )

        # Lesson C
        self._lessons['C'] = LessonContent(
            sign='C',
            description="Curve all fingers and thumb outward to form the shape of the letter 'C'.",
            meaning="Letter 'C' in the ASL manual alphabet.",
            reference_image="/assets/signs/C.png",
            optional_video="/assets/videos/C.mp4",
            difficulty="Easy",
            instructions=[
                "Curve your thumb and four fingers into an open arc.",
                "Align your fingertips opposite your thumb to mirror the letter 'C'.",
                "Turn palm slightly sideways so the C shape is clearly visible."
            ],
            common_mistakes=[
                "Closing the arc completely into an 'O'.",
                "Keeping fingers flat instead of curved."
            ],
            example_usage="Used for spelling words like 'CAT' or 'COMPUTER'.",
            course_module_relation="ASL Alphabet Foundations - Module 1"
        )

        # Lesson D
        self._lessons['D'] = LessonContent(
            sign='D',
            description="Extend the index finger straight upward while forming a circle with the thumb and remaining fingers.",
            meaning="Letter 'D' in the ASL manual alphabet.",
            reference_image="/assets/signs/D.png",
            optional_video="/assets/videos/D.mp4",
            difficulty="Easy",
            instructions=[
                "Extend your index finger straight up.",
                "Touch the tips of your middle, ring, and pinky fingers to your thumb tip.",
                "Form an open loop under the index finger."
            ],
            common_mistakes=[
                "Confusing with 'F' (in 'F', thumb touches index finger, remaining 3 fingers extended).",
                "Bending index finger downward."
            ],
            example_usage="Used for spelling words like 'DOG' or 'DREAM'.",
            course_module_relation="ASL Alphabet Foundations - Module 1"
        )

        # Lesson E
        self._lessons['E'] = LessonContent(
            sign='E',
            description="Curl all four fingers downward into the top of the palm while tucking the thumb tightly underneath.",
            meaning="Letter 'E' in the ASL manual alphabet.",
            reference_image="/assets/signs/E.png",
            optional_video="/assets/videos/E.mp4",
            difficulty="Intermediate",
            instructions=[
                "Bend all four fingers at the knuckles so fingertips rest above the palm.",
                "Tuck your thumb across underneath your fingertips.",
                "Ensure palm is facing forward."
            ],
            common_mistakes=[
                "Overlapping thumb over fingers (looks like 'S' or 'A').",
                "Flattish knuckles."
            ],
            example_usage="Used for spelling words like 'EAGLE' or 'EVERY'.",
            course_module_relation="ASL Alphabet Foundations - Module 1"
        )

    def get_lesson(self, sign_char: str) -> LessonContent:
        """Returns lesson content for given sign character, auto-generating scalable template for F-Z."""
        char = sign_char.upper()
        if char in self._lessons:
            return self._lessons[char]

        # Scalable dynamic generator for signs F-Z
        return LessonContent(
            sign=char,
            description=f"Standard ASL manual posture for letter '{char}'.",
            meaning=f"Letter '{char}' in the ASL manual alphabet.",
            reference_image=f"/assets/signs/{char}.png",
            optional_video=f"/assets/videos/{char}.mp4",
            difficulty="Intermediate",
            instructions=[
                f"Position dominant hand in front of camera at chest height.",
                f"Form hand configuration corresponding to letter '{char}'.",
                f"Hold hand posture steady inside tracking box."
            ],
            common_mistakes=[
                f"Dropping hand elevation out of tracking bounds.",
                f"Fingertip occlusion."
            ],
            example_usage=f"Used for spelling words starting with '{char}'.",
            course_module_relation="ASL Alphabet Foundations"
        )

    def list_all_lessons(self) -> List[LessonContent]:
        """Returns list of all 26 alphabet sign lessons A-Z."""
        all_signs = [chr(i) for i in range(ord('A'), ord('Z') + 1)]
        return [self.get_lesson(s) for s in all_signs]

# Global Lesson Registry Singleton
lesson_registry = LessonRegistry()
