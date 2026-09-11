import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../../api/client';
import { BookOpen, Video, Search, Sparkles, Lightbulb, CheckCircle2 } from 'lucide-react';
import { Button } from '../../components/common/Button';
import { Input } from '../../components/common/Input';
import { Card } from '../../components/common/Card';
import { Badge } from '../../components/common/Badge';
import { Modal } from '../../components/common/Modal';
import { Skeleton } from '../../components/common/Skeleton';
import { EmptyState } from '../../components/common/EmptyState';

export const Lessons = () => {
  const [courses, setCourses] = useState([]);
  const [lessons, setLessons] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedLesson, setSelectedLesson] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchLessonsData();
  }, []);

  const fetchLessonsData = async () => {
    try {
      const [coursesRes, lessonsRes] = await Promise.all([
        api.get('/lessons/courses'),
        api.get('/lessons/')
      ]);
      setCourses(coursesRes.data);
      setLessons(lessonsRes.data);
    } catch (err) {
      console.error("Failed to fetch lessons", err);
    } finally {
      setLoading(false);
    }
  };

  const filteredLessons = lessons.filter((lesson) =>
    lesson.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    lesson.sign_character.toLowerCase().includes(searchQuery.toLowerCase()) ||
    lesson.description.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="max-w-7xl mx-auto px-6 py-8 space-y-8 animate-fade-in">
      {/* Header Banner */}
      <Card hover={false} className="p-8 space-y-4 border-sky-500/20 bg-gradient-to-r from-slate-900 via-slate-900 to-sky-950/40">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-2">
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-xl bg-sky-500/10 border border-sky-500/20 text-sky-400">
                <BookOpen className="w-7 h-7" />
              </div>
              <h1 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight">
                ASL Manual Alphabet Curriculum
              </h1>
            </div>
            <p className="text-slate-400 text-sm max-w-2xl">
              Master all 26 letters of the American Sign Language manual alphabet through structured lessons, anatomical posture tips, and real-time AI webcam practice.
            </p>
          </div>
          <div className="w-full md:w-72">
            <Input
              icon={Search}
              placeholder="Search sign or letter..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
        </div>
      </Card>

      {/* Loading Skeleton */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <Skeleton count={6} className="h-44 w-full" />
        </div>
      ) : filteredLessons.length === 0 ? (
        <EmptyState
          title="No Lessons Match Your Search"
          description={`No sign language lessons found matching "${searchQuery}". Try searching for another letter or clear the filter.`}
          actionLabel="Clear Search Filter"
          onAction={() => setSearchQuery('')}
        />
      ) : (
        /* Lessons Grid */
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredLessons.map((lesson) => (
            <Card key={lesson.id} className="flex flex-col justify-between space-y-4">
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <Badge variant="info">Lesson #{lesson.order_index}</Badge>
                  <span className="w-10 h-10 rounded-xl bg-sky-500/20 text-sky-300 font-extrabold text-lg flex items-center justify-center border border-sky-500/30 shadow-inner">
                    {lesson.sign_character}
                  </span>
                </div>
                <h3 className="text-base font-bold text-white mt-1">{lesson.title}</h3>
                <p className="text-xs text-slate-400 leading-relaxed line-clamp-2">{lesson.description}</p>
              </div>

              <div className="pt-4 border-t border-slate-800 flex items-center justify-between gap-3">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setSelectedLesson(lesson)}
                >
                  View Details
                </Button>
                <Button
                  variant="primary"
                  size="sm"
                  icon={Video}
                  onClick={() => navigate('/practice')}
                >
                  Practice
                </Button>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Lesson Details Modal */}
      {selectedLesson && (
        <Modal
          isOpen={!!selectedLesson}
          onClose={() => setSelectedLesson(null)}
          title={`ASL Lesson: Sign '${selectedLesson.sign_character}'`}
          footer={
            <>
              <Button variant="outline" onClick={() => setSelectedLesson(null)}>
                Close
              </Button>
              <Button
                variant="primary"
                icon={Video}
                onClick={() => {
                  setSelectedLesson(null);
                  navigate('/practice');
                }}
              >
                Start Practice Session
              </Button>
            </>
          }
        >
          <div className="space-y-6">
            <div className="flex items-center gap-4 p-4 rounded-xl bg-slate-800/60 border border-slate-700/60">
              <div className="w-16 h-16 rounded-2xl bg-sky-500/20 text-sky-300 font-black text-3xl flex items-center justify-center border border-sky-500/40">
                {selectedLesson.sign_character}
              </div>
              <div>
                <h3 className="text-lg font-bold text-white">{selectedLesson.title}</h3>
                <p className="text-xs text-slate-400 mt-0.5">Order #{selectedLesson.order_index} in Alphabet Curriculum</p>
              </div>
            </div>

            <div className="space-y-2">
              <h4 className="text-xs font-bold uppercase text-slate-300 tracking-wider">Lesson Description</h4>
              <p className="text-sm text-slate-300 leading-relaxed">{selectedLesson.description}</p>
            </div>

            {selectedLesson.tips && (
              <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-200 space-y-2">
                <div className="flex items-center gap-2 font-bold text-xs uppercase tracking-wider text-amber-400">
                  <Lightbulb className="w-4 h-4" />
                  <span>Anatomical Posture Tip</span>
                </div>
                <p className="text-xs leading-relaxed">{selectedLesson.tips}</p>
              </div>
            )}
          </div>
        </Modal>
      )}
    </div>
  );
};
