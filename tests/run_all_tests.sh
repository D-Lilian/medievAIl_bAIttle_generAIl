#!/bin/bash
# Script de test rapide - Lance tous les tests de validation

echo "======================================================================"
echo "TESTS DE VALIDATION - MedievAIl BAIttle GenerAIl"
echo "======================================================================"
echo ""

echo "1. Test des spécifications..."
python test_specifications.py
SPEC_STATUS=$?

echo ""
echo "2. Test logique de jeu..."
python simple_game_logic.py > /tmp/game_test.log 2>&1
GAME_STATUS=$?
if [ $GAME_STATUS -eq 0 ]; then
    echo "   ✓ Logique de jeu OK"
    tail -5 /tmp/game_test.log
else
    echo "   ✗ Erreur dans la logique"
    cat /tmp/game_test.log
fi

echo ""
echo "3. Test mode headless..."
python ../View/terminal_view.py --test > /tmp/view_test.log 2>&1
VIEW_STATUS=$?
if [ $VIEW_STATUS -eq 0 ]; then
    echo "   ✓ Mode headless OK"
    tail -3 /tmp/view_test.log
else
    echo "   ✗ Erreur dans la vue"
    cat /tmp/view_test.log
fi

echo ""
echo "======================================================================"
echo "RÉSUMÉ"
echo "======================================================================"

TOTAL_FAILED=0

if [ $SPEC_STATUS -eq 0 ]; then
    echo "✓ Spécifications validées"
else
    echo "✗ Spécifications échouées"
    TOTAL_FAILED=$((TOTAL_FAILED + 1))
fi

if [ $GAME_STATUS -eq 0 ]; then
    echo "✓ Logique de jeu validée"
else
    echo "✗ Logique de jeu échouée"
    TOTAL_FAILED=$((TOTAL_FAILED + 1))
fi

if [ $VIEW_STATUS -eq 0 ]; then
    echo "✓ Vue terminal validée"
else
    echo "✗ Vue terminal échouée"
    TOTAL_FAILED=$((TOTAL_FAILED + 1))
fi

echo ""

if [ $TOTAL_FAILED -eq 0 ]; then
    echo "======================================================================"
    echo "✓ TOUS LES TESTS PASSENT - Projet prêt pour l'évaluation"
    echo "======================================================================"
    exit 0
else
    echo "======================================================================"
    echo "✗ $TOTAL_FAILED test(s) échoué(s)"
    echo "======================================================================"
    exit 1
fi
