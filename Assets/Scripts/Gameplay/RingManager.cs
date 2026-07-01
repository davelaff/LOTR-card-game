using UnityEngine;

namespace LOTRCardGame.Gameplay
{
    /// <summary>
    /// The One Ring mechanic — corruption track, activations, theft.
    /// Mirrors the Python engine/ring.py Ring class.
    /// </summary>
    public class RingManager : MonoBehaviour
    {
        public const int CorruptionWarning = 15;
        public const int CorruptionDanger = 20;
        public const int CorruptionLoss = 30;

        [Header("Corruption")]
        [Range(0, 30)]
        public int corruption;

        [Header("Bearer")]
        public string bearer = "fp"; // "fp" or "shadow"

        [Header("Activation (per turn)")]
        public bool fpActivatedThisTurn;
        public bool shadowActivatedThisTurn;

        [Header("Shadow Bearer Tracking")]
        public int shadowBearerTurns;

        // --- Corruption ---

        public void AddCorruption(int amount)
        {
            corruption = Mathf.Min(CorruptionLoss, corruption + amount);
        }

        /// <summary>
        /// Returns the losing player ("fp" or "shadow") or null if no loss.
        /// </summary>
        public string CheckCorruptionLoss()
        {
            if (corruption >= CorruptionLoss)
                return bearer;
            return null;
        }

        public string GetCorruptionStatus()
        {
            if (corruption >= CorruptionLoss)
                return "The Ring has consumed its bearer! GAME OVER.";
            if (corruption >= CorruptionDanger)
                return $"DANGER: {corruption}/{CorruptionLoss} — The Ring is close to consuming its bearer!";
            if (corruption >= CorruptionWarning)
                return $"WARNING: {corruption}/{CorruptionLoss} — The Ring grows heavy.";
            return $"Corruption: {corruption}/{CorruptionLoss}";
        }

        // --- Activation ---

        public bool CanActivateFP()
        {
            return bearer == "fp" && !fpActivatedThisTurn;
        }

        public bool CanActivateShadow()
        {
            return bearer == "shadow" && !shadowActivatedThisTurn;
        }

        /// <summary>
        /// Activate the Ring for Free Peoples. Returns the choice description, or null if can't activate.
        /// </summary>
        public string ActivateFP(string choice)
        {
            if (fpActivatedThisTurn || bearer != "fp")
                return null;
            fpActivatedThisTurn = true;
            AddCorruption(2);
            return choice;
        }

        /// <summary>
        /// Activate the Ring for Shadow. Returns the choice description, or null.
        /// Shadow bears the Ring more naturally: +1 corruption vs FP's +2.
        /// </summary>
        public string ActivateShadow(string choice)
        {
            if (shadowActivatedThisTurn || bearer != "shadow")
                return null;
            shadowActivatedThisTurn = true;
            AddCorruption(1);
            return choice;
        }

        // --- Theft & Recovery ---

        /// <summary>
        /// Shadow steals the Ring by killing the FP Hero.
        /// </summary>
        public void StealByShadow()
        {
            bearer = "shadow";
            shadowBearerTurns = 0;
            fpActivatedThisTurn = false;
            shadowActivatedThisTurn = false;
        }

        /// <summary>
        /// Free Peoples recovers the Ring by killing the Shadow Hero.
        /// </summary>
        public void RecoverByFP()
        {
            bearer = "fp";
            fpActivatedThisTurn = false;
            shadowActivatedThisTurn = false;
        }

        // --- Turn Bookends ---

        /// <summary>
        /// Called at start of each turn. Resets per-turn activation flags.
        /// </summary>
        public void StartTurn()
        {
            fpActivatedThisTurn = false;
            shadowActivatedThisTurn = false;
        }

        /// <summary>
        /// Called at end of each turn. Handles passive Shadow corruption.
        /// </summary>
        public void EndTurn(string player)
        {
            if (player == "shadow" && bearer == "shadow")
            {
                shadowBearerTurns++;
                if (shadowBearerTurns % 2 == 0)
                    AddCorruption(1);
            }
        }

        // --- Display ---

        public string CorruptionTrackDisplay
        {
            get
            {
                string bar = "";
                for (int i = 10; i <= 30; i += 10)
                {
                    if (corruption >= i)
                        bar += "█";
                    else if (corruption >= i - 5)
                        bar += "▒";
                    else
                        bar += "░";
                }
                return $"[{bar}] {corruption}/{CorruptionLoss}";
            }
        }
    }
}
