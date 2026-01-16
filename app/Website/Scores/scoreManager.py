from flask import render_template, Blueprint, flash, redirect, url_for, request, jsonify
from flask_login import login_required, current_user
from forms.scoreForm import ScoreForm
from repositories.assignmentRepo import AssignmentRepo

scores_bp = Blueprint("scores", __name__, static_folder="static", template_folder="templates")

repo = AssignmentRepo()

@scores_bp.route("/api/scores/", methods=["GET"])
@login_required
def getAllScores():
    """API endpoint to retrieve all scores for the current user"""
    user_id = current_user.user_id
    scores = repo.getAllScores(user_id)
    
    return jsonify({
        "status": "success",
        "scores": scores
    })

@scores_bp.route("/api/scores/<int:assignment_id>/", methods=["GET"])
@login_required
def getScore(assignment_id):
    """API endpoint to retrieve a specific assignment's score"""
    user_id = current_user.user_id
    score = repo.getScore(user_id, assignment_id)
    
    if score is None:
        # Check if assignment exists
        assignment = repo.getAssignmentById(user_id, assignment_id)
        if assignment is None:
            return jsonify({
                "status": "error",
                "message": "Assignment not found"
            }), 404
        
        # Assignment exists but no score yet
        return jsonify({
            "status": "success",
            "assignment_id": assignment_id,
            "score": None
        })
    
    return jsonify({
        "status": "success",
        "assignment_id": assignment_id,
        "score": score
    })

@scores_bp.route("/api/scores/<int:assignment_id>/", methods=["POST", "PUT"])
@login_required
def updateScore(assignment_id):
    """API endpoint to update an assignment's score"""
    user_id = current_user.user_id
    
    # Get score from request
    data = request.get_json()
    if not data or 'score' not in data:
        return jsonify({
            "status": "error",
            "message": "Score is required"
        }), 400
    
    try:
        score = float(data['score'])
        if score < 0:
            return jsonify({
                "status": "error",
                "message": "Score must be non-negative"
            }), 400
    except (ValueError, TypeError):
        return jsonify({
            "status": "error",
            "message": "Invalid score format"
        }), 400
    
    # Update the score
    success = repo.updateScore(user_id, assignment_id, score)
    
    if success:
        return jsonify({
            "status": "success",
            "message": "Score updated successfully",
            "assignment_id": assignment_id,
            "score": score
        })
    else:
        return jsonify({
            "status": "error",
            "message": "Assignment not found or update failed"
        }), 404

@scores_bp.route("/scores/update/<int:assignment_id>/", methods=["GET", "POST"])
@login_required
def updateScoreForm(assignment_id):
    """Web form endpoint to update an assignment's score"""
    user_id = current_user.user_id
    form = ScoreForm()
    
    # Get the assignment
    assignment = repo.getAssignmentById(user_id, assignment_id)
    if assignment is None:
        flash("Assignment not found", "error")
        return redirect(url_for("mainPage.dashboard"))
    
    if form.validate_on_submit():
        score = form.score.data
        success = repo.updateScore(user_id, assignment_id, score)
        
        if success:
            flash(f"Score updated successfully for '{assignment.title}'", "success")
            return redirect(url_for("mainPage.dashboard"))
        else:
            flash("Failed to update score", "error")
    
    # Pre-populate form with existing score
    if request.method == "GET":
        form.assignment_id.data = assignment_id
        form.score.data = assignment.score
    
    return render_template("updateScore.html", form=form, assignment=assignment)
