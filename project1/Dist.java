import java.util.Random;

public class Dist {

    public static final long FNV_OFFSET_BASIS_64 = 0xCBF29CE484222325L;
    public static final long FNV_PRIME_64 = 1099511628211L;

    private Random random;
    private long max;
    private double mean;
    private double stddev;
    
    public Dist() {
        random = new Random(1337);
        max = 20000;
        mean = max / 2;
        stddev = max / 13;
    }

    public long nextValue() {
        long next = (long) (random.nextGaussian() * stddev + mean);
        next = fnvhash64(next) % max;
        return next;
    }
    
    public static void main(String[] args) {
        Dist dist = new Dist();
        for (int i = 0; i < 100000; i++) {
            System.out.println(dist.nextValue());
        }
    }

     public static long fnvhash64(long val) {
        long hashval = FNV_OFFSET_BASIS_64;

        for (int i = 0; i < 8; i++) {
            long octet = val & 0x00ff;
            val = val >> 8;

            hashval = hashval ^ octet;
            hashval = hashval * FNV_PRIME_64;
            //hashval = hashval ^ octet;
        }
        return Math.abs(hashval);
    }
}
