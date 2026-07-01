using UnityEngine;
using System.Collections.Generic;
using LOTRCardGame.Data;

namespace LOTRCardGame.Gameplay
{
    /// <summary>
    /// Runtime state for an ally on the board. Wraps a CardData ScriptableObject
    /// reference with mutable game state (toughness, tapped, temp bonuses, etc.).
    /// </summary>
    [System.Serializable]
    public class BoardAlly
    {
        [Header("Card Reference")]
        public CardData card;

        [Header("Runtime State")]
        public int currentToughness;
        public int turnEntered;
        public bool tapped;
        public bool hasAttackedThisTurn;
        public bool hasMovedThisTurn;
        public bool hasUsedAbilityThisTurn;

        [Header("Temporary Modifiers")]
        public int tempPowerBonus;
        public int tempToughnessBonus;

        [Header("Attachments")]
        public List<CardData> artifacts = new List<CardData>();

        // --- Computed Properties ---

        public bool IsAlive => currentToughness > 0;

        public int EffectivePower => (card != null ? card.power : 0) + tempPowerBonus;

        public int EffectiveToughness => (card != null ? card.toughness : 0) + tempToughnessBonus;

        public bool HasKeyword(string keyword) =>
            card != null && card.keywords != null && card.keywords.Contains(keyword);

        public bool HasRanged => HasKeyword("Ranged");
        public bool HasCharge => HasKeyword("Charge");
        public bool HasAmbush => HasKeyword("Ambush");

        // --- Action Checks ---

        public bool CanAttack() => !tapped && !hasAttackedThisTurn && IsAlive;

        public bool CanMove() => !tapped && !hasMovedThisTurn && IsAlive;

        public bool CanUseAbility() => !hasUsedAbilityThisTurn && IsAlive;

        // --- State Modifiers ---

        public void TakeDamage(int amount)
        {
            currentToughness = Mathf.Max(0, currentToughness - amount);
        }

        public void Heal(int amount)
        {
            currentToughness += amount;
        }

        public void ClearTempBonuses()
        {
            tempPowerBonus = 0;
            tempToughnessBonus = 0;
        }

        /// <summary>
        /// Reset per-turn flags (called during Start Phase untap).
        /// </summary>
        public void Untap()
        {
            tapped = false;
            hasAttackedThisTurn = false;
            hasMovedThisTurn = false;
            hasUsedAbilityThisTurn = false;
        }
    }
}
