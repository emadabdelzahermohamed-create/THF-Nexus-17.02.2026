package com.topherofit.rescue;

import org.junit.Test;
import java.util.*;
import static org.junit.Assert.*;

public class ProductRegistryTest {
    @Test public void registryContainsEveryRescueProductWithUniquePackages() {
        Map<String, ProductRegistry.Product> products = ProductRegistry.all();
        Set<String> expected = new LinkedHashSet<>(Arrays.asList("hub","fitness","wave","arena","ruinsciv","endciv","tokenops","publisher","vault"));
        assertEquals(expected, products.keySet());
        Set<String> packages = new HashSet<>();
        for (ProductRegistry.Product p : products.values()) {
            assertNotNull(p.title);
            assertTrue(p.packageId.startsWith("com.topherofit."));
            assertTrue("duplicate package " + p.packageId, packages.add(p.packageId));
        }
    }
}
