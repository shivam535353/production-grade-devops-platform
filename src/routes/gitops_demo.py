@gitops_demo_bp.route("/gitops-demo", methods=["GET"])
def gitops_demo():
    # INTENTIONAL BUG — simulate failed deployment
    result = 1 / 0

    return jsonify({
        "message": "This will never reach here"
    }), 200
